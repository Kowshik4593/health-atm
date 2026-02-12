# backend/app/routes/process.py
"""
Processing Route for HealthATM.

Triggers AI analysis pipeline for an uploaded CT scan.

Endpoints:
- POST /process/case/{case_id} - Trigger ML processing
- GET /process/status/{case_id} - Get processing status
"""

import os
import json
import traceback
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks, Header
from app.supabase_client import supabase
from app.audit import log
from app.notifications import notify

router = APIRouter(prefix="/process", tags=["process"])

# Staging directory where uploads are saved
STAGING_DIR = Path(__file__).parent.parent / "uploads"
OUTPUTS_DIR = Path(__file__).parent.parent / "outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# Background Processing Task
# =============================================================================

def run_ml_pipeline(case_id: str, patient_id: str = None):
    """
    Background task that runs the full ML pipeline.

    Steps:
    1. Update status to 'processing'
    2. Find the uploaded scan
    3. Run inference
    4. Save findings.json
    5. Generate reports
    6. Update status to 'completed' (or 'failed')
    """
    try:
        # 1. Update status
        supabase.table("patient_ct_scans").update(
            {"status": "processing"}
        ).eq("id", case_id).execute()

        print(f"[process] Starting ML pipeline for case: {case_id}")

        # 2. Find uploaded scan
        case_dir = STAGING_DIR / case_id
        dicom_dir = case_dir / "dicom"
        scan_path = None
        is_dicom = False

        if dicom_dir.exists() and any(dicom_dir.rglob("*.dcm")):
            # Find the actual DICOM directory (might be nested)
            for root, dirs, files in os.walk(dicom_dir):
                if any(f.endswith(".dcm") for f in files):
                    scan_path = root
                    is_dicom = True
                    break
        elif (case_dir / "scan.zip").exists():
            scan_path = str(case_dir / "scan.zip")
        elif (case_dir / "scan.npy").exists():
            scan_path = str(case_dir / "scan.npy")
        elif (case_dir / "scan.npz").exists():
            scan_path = str(case_dir / "scan.npz")
        elif (case_dir / "scan.dcm").exists():
            scan_path = str(case_dir / "scan.dcm")
            is_dicom = True

        if not scan_path:
            raise FileNotFoundError(f"No scan data found for case: {case_id}")

        # 3. Run inference
        output_dir = str(OUTPUTS_DIR / case_id)
        os.makedirs(output_dir, exist_ok=True)

        from app.services.inference_service import analyze_scan
        findings = analyze_scan(
            case_id=case_id,
            input_path=scan_path,
            output_dir=output_dir,
            is_dicom=is_dicom
        )

        # 4. Save findings.json to known location
        findings_path = os.path.join(output_dir, f"{case_id}_findings.json")
        with open(findings_path, "w", encoding="utf-8") as f:
            json.dump(findings, f, indent=2, ensure_ascii=False)

        # 5. Upload findings.json to Supabase Storage
        json_bytes = json.dumps(findings, indent=2).encode("utf-8")
        try:
            supabase.storage.from_("ml_json").upload(
                f"{case_id}/findings.json",
                json_bytes,
                file_options={"content-type": "application/json"}
            )
        except Exception as e:
            print(f"[process] Supabase JSON upload skipped: {e}")

        # 6. Store results in DB
        result_data = {
            "scan_id": case_id,
            "json_path": f"ml_json/{case_id}/findings.json",
            "ai_score": findings.get("nodules", [{}])[0].get("prob_malignant", 0) if findings.get("nodules") else 0,
            "num_nodules": findings.get("num_nodules", 0),
            "risk_label": "high" if any(n.get("prob_malignant", 0) >= 0.7 for n in findings.get("nodules", [])) else (
                "moderate" if any(n.get("prob_malignant", 0) >= 0.4 for n in findings.get("nodules", [])) else "low"
            ),
            "impression": findings.get("impression", ""),
        }

        try:
            supabase.table("scan_results").upsert(
                result_data, on_conflict="scan_id"
            ).execute()
        except Exception as e:
            print(f"[process] DB results insert error: {e}")

        # 7. Generate reports (try, don't fail pipeline)
        try:
            from app.reporter import generate_all_reports
            from app.storage_service import save_local

            reports = generate_all_reports(
                findings_path,
                patient_lang="en",
                include_hindi=True
            )

                # Save locally and update DB
            paths_update = {}
            for rtype, rpath in reports.items():
                if "error" not in rtype and os.path.exists(rpath):
                    with open(rpath, "rb") as rf:
                        content = rf.read()
                    filename = os.path.basename(rpath)
                    
                    # 1. Save locally (backup)
                    save_local(case_id, filename, content)

                    # 2. Upload to Supabase 'reports' bucket
                    storage_path = f"{case_id}/{filename}"
                    try:
                        supabase.storage.from_("reports").upload(
                            storage_path,
                            content,
                            file_options={"content-type": "application/pdf"}
                        )
                        print(f"[process] Uploaded report to Supabase: {storage_path}")

                        # Map to DB columns
                        if "clinician" in rtype:
                            paths_update["clinician_pdf"] = storage_path
                        elif "patient_en" in rtype:
                            paths_update["patient_pdf"] = storage_path

                    except Exception as e:
                         print(f"[process] Report upload error ({filename}): {e}")

            # 3. Update scan_results table with report paths
            if paths_update:
                try:
                    supabase.table("scan_results").update(paths_update).eq("scan_id", case_id).execute()
                    print(f"[process] Updated scan_results with report paths: {list(paths_update.keys())}")
                except Exception as e:
                    print(f"[process] DB update error for reports: {e}")

            print(f"[process] [OK] Reports generated: {list(reports.keys())}")

        except Exception as e:
            print(f"[process] [WARN] Report generation skipped: {e}")

        # 8. Update status to completed
        supabase.table("patient_ct_scans").update(
            {"status": "completed"}
        ).eq("id", case_id).execute()

        # 9. Notify patient
        if patient_id:
            notify(patient_id, f"Your CT scan analysis is complete! Case: {case_id[:8]}...")

        print(f"[process] [OK] Pipeline complete for case: {case_id}")
        log(patient_id, "ml_pipeline_complete", {
            "case_id": case_id,
            "num_nodules": findings.get("num_nodules", 0),
            "processing_time": findings.get("processing_time_seconds", 0)
        })

    except Exception as e:
        # Update status to failed
        print(f"[process] [FAIL] Pipeline failed for {case_id}: {e}")
        traceback.print_exc()

        try:
            supabase.table("patient_ct_scans").update(
                {"status": "failed"}
            ).eq("id", case_id).execute()
        except Exception:
            pass

        if patient_id:
            notify(patient_id, f"CT scan analysis encountered an error. Our team has been notified. Case: {case_id[:8]}...")

        log(patient_id, "ml_pipeline_failed", {
            "case_id": case_id,
            "error": str(e)
        }, severity="error")


# =============================================================================
# API Endpoints
# =============================================================================

@router.post("/case/{case_id}")
async def trigger_processing(
    case_id: str,
    background_tasks: BackgroundTasks,
    x_user_id: Optional[str] = Header(None, alias="x-user-id"),
    x_user_role: Optional[str] = Header(None, alias="x-user-role"),
):
    """
    Trigger ML processing for a case.

    This starts the AI pipeline in the background and returns immediately.
    The frontend should poll /cases/{case_id} to check status.
    """
    # Verify case exists
    try:
        case = supabase.table("patient_ct_scans").select("*").eq("id", case_id).single().execute()
        if not case.data:
            raise HTTPException(status_code=404, detail="Case not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Case not found: {str(e)}")

    patient_id = case.data.get("patient_id", x_user_id)

    # Check if already processing or completed
    current_status = case.data.get("status")
    if current_status == "processing":
        return {"success": True, "message": "Already processing", "status": "processing"}
    if current_status == "completed":
        return {"success": True, "message": "Already completed", "status": "completed"}

    # Start background processing
    background_tasks.add_task(run_ml_pipeline, case_id, patient_id)

    return {
        "success": True,
        "message": "Processing started",
        "case_id": case_id,
        "status": "processing"
    }


@router.get("/status/{case_id}")
async def get_processing_status(case_id: str):
    """Get current processing status for a case."""
    try:
        case = supabase.table("patient_ct_scans").select("status").eq("id", case_id).single().execute()
        if not case.data:
            raise HTTPException(status_code=404, detail="Case not found")

        return {
            "case_id": case_id,
            "status": case.data.get("status", "unknown")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
