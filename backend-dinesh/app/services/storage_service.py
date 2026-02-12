# app/services/storage_service.py
import json
import os
from pathlib import Path
import requests
import tempfile
from app.supabase_client import supabase
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
# bucket root (already used in your code): 'ct_scans'
DEFAULT_BUCKET = "ct_scans"

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    # Don't crash import-time; raise when trying to upload
    pass
class StorageService:

    @staticmethod
    def upload_file(bucket: str, path: str, content: bytes, content_type: str):
        """
        Compatible with your old call:
            upload_file(bucket="ct_scans", path="case/file.zip", content=data, content_type="application/zip")
        """

        if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
            raise RuntimeError(
                "Environment vars SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set."
            )

        # Create a temp file so we can stream it
        temp_dir = Path(tempfile.mkdtemp())
        temp_file = temp_dir / Path(path).name
        temp_file.write_bytes(content)

        upload_url = f"{SUPABASE_URL.rstrip('/')}/storage/v1/object/{bucket}/{path}"

        headers = {
            "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
            "x-upsert": "true",
            "Content-Type": content_type or "application/octet-stream"
        }

        print(f"[UPLOAD] Streaming file → {upload_url}")

        def file_stream():
            with open(temp_file, "rb") as f:
                while chunk := f.read(1024 * 1024):  # 1MB chunks
                    yield chunk

        # Perform streaming upload
        resp = requests.put(upload_url, headers=headers, data=file_stream(), timeout=120)

        if resp.status_code not in (200, 201, 204):
            raise Exception(f"Upload failed ({resp.status_code}): {resp.text}")

        # Cleanup
        try:
            temp_file.unlink()
            temp_dir.rmdir()
        except:
            pass

        print("[UPLOAD] Success.")
        return True
    @staticmethod
    def upload_file_auto(bucket: str, storage_key: str, file_path: Path, content_type: str = "application/zip"):
        # wrapper with sane defaults
        return StorageService.upload_file(bucket, storage_key, file_path, content_type=content_type, timeout_seconds=120)

    @staticmethod
    def upload_json(case_id: str, findings_json: dict):
        path = f"{case_id}/findings.json"
        supabase.storage.from_("ml_json").upload(
            path,
            json.dumps(findings_json).encode(),
            {"content-type": "application/json"}
        )
        return path

    @staticmethod
    def upload_pdf(case_id: str, pdf_bytes: bytes, kind: str):
        path = f"{case_id}/{kind}.pdf"
        supabase.storage.from_("reports").upload(
            path, pdf_bytes, {"content-type": "application/pdf"}
        )
        return path
