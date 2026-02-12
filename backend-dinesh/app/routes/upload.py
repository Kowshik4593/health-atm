# app/routes/upload.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.deps import get_current_user
from app.services.case_service import CaseService
from app.services.storage_service import StorageService

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("/scan")
async def upload_scan(file: UploadFile = File(...), user = Depends(get_current_user)):
    if user.role != "patient":
        raise HTTPException(403, "Only patients can upload scans")

    data = await file.read()

    # Create case first
    case = CaseService.create_case(
        patient_id=user.id,
        storage_path="pending"
    )
    case_id = case["id"]

    storage_path = f"{case_id}/{file.filename}"

    StorageService.upload_file(
        bucket="ct_scans",
        path=storage_path,
        content=data,
        content_type=file.content_type
    )

    CaseService.update_storage_path(case_id, storage_path)

    return {"case_id": case_id, "storage_path": storage_path}
