# backend/app/routes/patient.py
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from uuid import uuid4
from app.supabase_client import supabase
from app.audit import log
from app.notifications import notify

router = APIRouter(prefix="/patient", tags=["patient"])

@router.post("/upload-ct")
async def upload_ct(patient_id: str, file: UploadFile = File(...)):
    """
    Patient uploads CT file. We create a new scan record and store file in ct_scans bucket.
    Returns: case_id
    """
    case_id = str(uuid4())
    file_bytes = await file.read()
    ext = file.filename.split(".")[-1] if file.filename else "zip"
    storage_path = f"{case_id}/scan.{ext}"

    

    # insert DB row
    supabase.table("patient_ct_scans").insert({
        "id": case_id,
        "patient_id": patient_id,
        "storage_path": storage_path,
        "status": "uploaded"
    }).execute()

    log(patient_id, "upload_ct", {"case_id": case_id, "storage_path": storage_path})
    notify(patient_id, f"CT uploaded (case: {case_id}). Processing will start shortly.")
    return {"case_id": case_id, "storage_path": storage_path}
