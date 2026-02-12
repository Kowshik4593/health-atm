# app/routes/process.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.deps import get_current_user
from app.services.case_service import CaseService
from app.services.ml_service import MLService

router = APIRouter(prefix="/process", tags=["process"])

@router.post("/case/{case_id}")
def process_case(case_id: str, background_tasks: BackgroundTasks, user = Depends(get_current_user)):
    # --- FIX: Added "patient" to allowed roles ---
    if user.role not in ("operator", "doctor", "patient"):
        raise HTTPException(403, "Not allowed")

    case = CaseService.get_case(case_id)
    if not case:
        raise HTTPException(404, "Case not found")

    # Update status immediately so UI knows it started
    CaseService.update_status(case_id, "processing")

    # --- FIX: Run ML in Background (Non-blocking) ---
    # This prevents the request from timing out while ML runs for 10 mins
    background_tasks.add_task(run_ml_task, case_id, case["storage_path"])

    return {"status": "processing"}

def run_ml_task(case_id: str, storage_path: str):
    """Wrapper to handle errors during background execution"""
    try:
        MLService.run_pipeline(case_id, storage_path)
    except Exception as e:
        print(f"Background ML Error: {e}")
        CaseService.update_status(case_id, "failed")