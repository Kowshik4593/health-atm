from fastapi import APIRouter, Depends, HTTPException
from app.deps import get_current_user
from app.services.case_service import CaseService

router = APIRouter(prefix="/cases", tags=["cases"])


# 1️⃣ MUST COME BEFORE /{case_id}
@router.get("/patient/{patient_id}")
def patient_cases(patient_id: str, user=Depends(get_current_user)):
    if user.role == "patient" and user.id != patient_id:
        raise HTTPException(403, "Forbidden")
    return CaseService.get_patient_cases(patient_id)


# 2️⃣ DOCTOR ROUTE
@router.get("/unassigned")
def unassigned(user=Depends(get_current_user)):
    if user.role != "doctor":
        raise HTTPException(403, "Forbidden")
    return CaseService.get_unassigned_cases()


# 3️⃣ CASE DETAILS (must be LAST)
@router.get("/{case_id}")
def get_case(case_id: str, user=Depends(get_current_user)):
    case = CaseService.get_case(case_id)
    if not case:
        raise HTTPException(404, "Case not found")

    if user.role == "patient" and case["patient_id"] != user.id:
        raise HTTPException(403, "Forbidden")

    return case
