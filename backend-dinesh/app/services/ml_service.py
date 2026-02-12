# app/services/ml_service.py
import zipfile
import tempfile
from pathlib import Path
import subprocess
import shutil
import sys
import json
import time

from app.supabase_client import supabase
from app.services.scan_result_service import ScanResultService

class MLService:

    # -------------------------------------------------------
    # 1) DOWNLOAD ZIP INTO TEMP DIRECTORY
    # -------------------------------------------------------
    @staticmethod
    def _download_zip_to_temp(storage_path: str):
        bucket = "ct_scans"
        print(f"[ML] Downloading {storage_path} from bucket {bucket}")

        resp = supabase.storage.from_(bucket).download(storage_path)
        if resp is None:
            raise Exception("Failed to download CT scan ZIP from Supabase")

        temp_root = Path(tempfile.mkdtemp())
        zip_path = temp_root / "scan.zip"
        zip_path.write_bytes(resp)

        return temp_root, zip_path

    # -------------------------------------------------------
    # 2) EXTRACT ZIP
    # -------------------------------------------------------
    @staticmethod
    def _extract_zip(zip_path: Path):
        extract_dir = zip_path.parent / "extracted"
        extract_dir.mkdir(exist_ok=True)

        print(f"[ML] Extracting ZIP -> {extract_dir}")
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(extract_dir)

        # Handle case of one nested folder
        subitems = [p for p in extract_dir.iterdir() if p.exists()]
        if len(subitems) == 1 and subitems[0].is_dir():
            print(f"[ML] Nested folder detected: {subitems[0]}")
            return subitems[0]

        return extract_dir

    # -------------------------------------------------------
    # 3) FIND pipeline.py
    # -------------------------------------------------------
    @staticmethod
    def _find_pipeline_path():
        # backend-dinesh directory
        backend_root = Path(__file__).resolve().parents[2]

        candidates = [
            backend_root / "ml" / "pipeline.py",
            backend_root / "backend-dinesh" / "ml" / "pipeline.py",
            backend_root.parent / "backend-dinesh" / "ml" / "pipeline.py",
        ]

        for p in candidates:
            print(f"[ML] Checking pipeline candidate: {p}")
            if p.exists():
                print(f"[ML] Using pipeline at: {p}")
                return p

        raise FileNotFoundError(
            "pipeline.py not found. Checked:\n" +
            "\n".join(str(x) for x in candidates)
        )

    # -------------------------------------------------------
    # 4) RUN PIPELINE + UPLOAD findings.json
    # -------------------------------------------------------
    @staticmethod
    def run_pipeline(case_id: str, storage_path: str):

        # STEP 1 — DOWNLOAD ZIP
        temp_root, zip_path = MLService._download_zip_to_temp(storage_path)

        try:
            # STEP 2 — EXTRACT
            extracted_folder = MLService._extract_zip(zip_path)

            # STEP 3 — LOCATE pipeline.py
            pipeline_path = MLService._find_pipeline_path()

            # STEP 4 — RUN PIPELINE SCRIPT
            cmd = [
                sys.executable,         # use venv python.exe
                str(pipeline_path),
                "--study_folder", str(extracted_folder),
                "--study_id", case_id
            ]

            print("[ML] Running pipeline command:")
            print("  " + " ".join(cmd))

            proc = subprocess.run(cmd, capture_output=True, text=True)

            print("[ML] pipeline stdout:\n", proc.stdout)

            if proc.returncode != 0:
                print("[ML] pipeline stderr:\n", proc.stderr)
                raise Exception(f"Pipeline failed (rc={proc.returncode})")

            print("[ML] Pipeline completed successfully.")

            # -------------------------------------------------------
            # STEP 5 — FIND findings.json (ABSOLUTE PATH FIX)
            # -------------------------------------------------------
            backend_root = Path(__file__).resolve().parents[2]

            possible_paths = [
                backend_root / "outputs" / f"{case_id}_findings.json",
                backend_root.parent / "backend-dinesh" / "outputs" / f"{case_id}_findings.json",
                backend_root / "backend-dinesh" / "outputs" / f"{case_id}_findings.json",
            ]

            json_local_path = None
            for p in possible_paths:
                print(f"[ML] Checking for findings.json at: {p}")
                if p.exists():
                    json_local_path = p
                    print(f"[ML] FOUND findings.json at: {p}")
                    break

            if json_local_path is None:
                raise Exception("Pipeline did not produce findings.json")

            # -------------------------------------------------------
            # STEP 6 — UPLOAD JSON TO SUPABASE ml_json
            # Robustly handle existing resource (Duplicate)
            # -------------------------------------------------------
            storage_key = f"{case_id}/findings.json"
            json_bytes = json_local_path.read_bytes()

            print(f"[ML] Uploading JSON → ml_json/{storage_key}")

            try:
                # first attempt: upload
                supabase.storage.from_("ml_json").upload(
                    storage_key,
                    json_bytes,
                    {"content-type": "application/json"}
                )
                print("[ML] Upload succeeded (new object).")

            except Exception as e:
                # detect duplicate / already exists error message
                msg = str(e)
                print(f"[ML] Upload error: {msg}")

                duplicate_indicators = ["Duplicate", "already exists", "The resource already exists"]
                if any(indicator in msg for indicator in duplicate_indicators):
                    # Try removing existing object and re-uploading
                    try:
                        print("[ML] Attempting to remove existing object and re-upload...")
                        supabase.storage.from_("ml_json").remove(storage_key)
                        # small delay to ensure remote is consistent
                        time.sleep(0.3)
                        supabase.storage.from_("ml_json").upload(
                            storage_key,
                            json_bytes,
                            {"content-type": "application/json"}
                        )
                        print("[ML] Re-upload succeeded after removing existing object.")
                    except Exception as e2:
                        # final fallback: report detailed failure
                        raise Exception({
                            "statusCode": 500,
                            "error": "UploadFailed",
                            "message": f"Upload failed after attempting remove. original: {msg}, remove error: {e2}"
                        })
                else:
                    # not a duplicate error — re-raise with context
                    raise Exception({
                        "statusCode": 500,
                        "error": "UploadFailed",
                        "message": f"Upload failed: {msg}"
                    })

            # -------------------------------------------------------
            # STEP 7 — UPDATE scan_results TABLE (UPSERT)
            # -------------------------------------------------------
            # Note: upsert_result should perform an upsert (insert or update),
            # so it will not fail on duplicate DB rows.
            ScanResultService.upsert_result(case_id, storage_key)
            print(f"[ML] Updated scan_results for case {case_id}")

            return True

        finally:
            # Clean temp folder
            try:
                shutil.rmtree(temp_root)
                print(f"[ML] Cleaned temp folder {temp_root}")
            except Exception as e:
                print(f"[ML] Could not clean temp folder: {e}")
