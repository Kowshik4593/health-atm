# app/routes/doctor.py
from fastapi import APIRouter, Depends, HTTPException
from app.deps import get_current_user
from app.services.assignment_service import AssignmentService
from app.services.notification_service import NotificationService
from app.supabase_client import supabase
from app.services.case_service import CaseService

router = APIRouter(prefix="/doctor", tags=["doctor"])

@router.post("/accept/{case_id}")
def accept_case(case_id: str, user=Depends(get_current_user)):
    if user.role != "doctor":
        raise HTTPException(403, "Only doctors can accept scans")

    assignment = CaseService.assign_doctor(case_id, user.id)

    return {
        "id": assignment["id"],          # ★ MOST IMPORTANT
        "scan_id": case_id,
        "doctor_id": user.id,
        "status": assignment["status"],
        "accepted_at": assignment["accepted_at"]
    }

@router.get("/assignment/{case_id}")
def get_assignment(case_id: str, user=Depends(get_current_user)):
    assignment = CaseService.get_assignment_by_scan(case_id)
    if not assignment:
        raise HTTPException(404, "Assignment not found")
    return assignment

