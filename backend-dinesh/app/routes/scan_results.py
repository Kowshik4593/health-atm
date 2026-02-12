# app/routes/scan_results.py
from fastapi import APIRouter, Depends, HTTPException
from app.services.scan_result_service import ScanResultService
from app.deps import get_current_user

router = APIRouter(prefix="/scan_results", tags=["scan_results"])

@router.get("/{scan_id}")
def get_scan_result(scan_id: str, user = Depends(get_current_user)):
    result = ScanResultService.get_result(scan_id)

    if not result:
        raise HTTPException(404, "Not Found")

    return result
