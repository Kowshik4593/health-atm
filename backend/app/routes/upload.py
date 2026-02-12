# backend/app/routes/upload.py
"""
Upload Route for HealthATM.

Handles CT scan file uploads from both patients and operators.
Stores the file in Supabase Storage and creates DB records.

Endpoints:
- POST /upload/scan - Upload a CT scan (.zip, .npy, .dcm)
"""

import os
import io
import zipfile
import tempfile
from uuid import uuid4
from pathlib import Path
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, Header, HTTPException
from app.supabase_client import supabase
from app.audit import log
from app.notifications import notify


router = APIRouter(prefix="/upload", tags=["upload"])


# =============================================================================
# Helpers
# =============================================================================

ALLOWED_EXTENSIONS = {".zip", ".npy", ".npz", ".dcm"}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB

# Local staging directory for uploaded files
STAGING_DIR = Path(__file__).parent.parent / "uploads"
STAGING_DIR.mkdir(parents=True, exist_ok=True)


def _validate_file(file: UploadFile) -> str:
    """Validate uploaded file and return extension."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    return ext


# =============================================================================
# Upload Endpoint
# =============================================================================

@router.post("/scan")
async def upload_scan(
    file: UploadFile = File(...),
    x_user_id: Optional[str] = Header(None, alias="x-user-id"),
    x_user_role: Optional[str] = Header(None, alias="x-user-role"),
):
    """
    Upload a CT scan file for analysis.

    Accepts: .zip (DICOM series), .npy/.npz (preprocessed), .dcm (single DICOM)

    Flow:
    1. Validate the file
    2. Create a new case record in patient_ct_scans
    3. Save file locally for processing
    4. Store path reference in Supabase Storage (if available)
    5. Return case_id for polling

    Headers:
        x-user-id: The patient ID
        x-user-role: User role (patient/operator/doctor)
    """
    # 1. Identify patient
    patient_id = x_user_id
    if not patient_id:
        raise HTTPException(status_code=400, detail="Missing x-user-id header")

    # 2. Validate file
    ext = _validate_file(file)

    # 3. Generate case ID
    case_id = str(uuid4())

    # 4. Read file content
    try:
        file_bytes = await file.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")

    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty file uploaded")

    # 5. Save locally for ML processing
    case_dir = STAGING_DIR / case_id
    case_dir.mkdir(parents=True, exist_ok=True)

    local_path = case_dir / f"scan{ext}"
    with open(local_path, "wb") as f:
        f.write(file_bytes)

    # If ZIP, extract DICOM files
    is_dicom = False
    if ext == ".zip":
        try:
            dicom_dir = case_dir / "dicom"
            dicom_dir.mkdir(exist_ok=True)
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
                zf.extractall(dicom_dir)
            is_dicom = True
        except zipfile.BadZipFile:
            # Not a zip, treat as binary
            pass

    # 6. Try uploading to Supabase Storage
    storage_path = f"{case_id}/scan{ext}"
    supabase_uploaded = False
    try:
        supabase.storage.from_("ct_scans").upload(
            storage_path,
            file_bytes,
            file_options={"content-type": file.content_type or "application/octet-stream"}
        )
        supabase_uploaded = True
    except Exception as e:
        print(f"[upload] Supabase storage upload skipped: {e}")

    # 7. Create DB record
    try:
        scan_data = {
            "id": case_id,
            "patient_id": patient_id,
            "storage_path": storage_path,
            "status": "uploaded",
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
        }

        supabase.table("patient_ct_scans").insert(scan_data).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create scan record: {str(e)}")

    # 8. Audit & Notify
    log(patient_id, "upload_scan", {
        "case_id": case_id,
        "filename": file.filename,
        "size_bytes": len(file_bytes),
        "extension": ext,
        "supabase_uploaded": supabase_uploaded,
        "is_dicom": is_dicom,
    })
    notify(patient_id, f"Your CT scan has been uploaded (Case: {case_id[:8]}...). Analysis will begin shortly.")

    return {
        "success": True,
        "case_id": case_id,
        "storage_path": storage_path,
        "status": "uploaded",
        "file_size": len(file_bytes),
        "is_dicom": is_dicom,
    }
