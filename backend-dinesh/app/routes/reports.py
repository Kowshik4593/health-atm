# app/routes/reports.py

from fastapi import APIRouter, Depends, HTTPException, Query
from app.deps import get_current_user
from app.services.case_service import CaseService
from app.services.scan_result_service import ScanResultService

router = APIRouter(prefix="/cases/reports", tags=["Reports"])

# --------------------------------------------------------------
# ROLE-BASED REPORT ACCESS RULES:
# --------------------------------------------------------------
# Patient  → only patient_report.pdf
# Doctor   → only clinician_report.pdf
# Operator → only patient_report.pdf
# --------------------------------------------------------------


@router.get("/{case_id}")
def get_report(case_id: str, user_id: str = Query(...), user=Depends(get_current_user)):
    """
    Returns the correct report URL based on user role.

    Response examples:

    Patient:
    {
        "patient_report": {
            "url": "/local_reports/<case_id>/patient_report.pdf"
        }
    }

    Doctor:
    {
        "clinician_report": {
            "url": "/local_reports/<case_id>/clinician_report.pdf"
        }
    }

    Operator:
    {
        "patient_report": {
            "url": "/local_reports/<case_id>/patient_report.pdf"
        }
    }
    """

    # ----------------------------------------------------------------------
    # VALIDATE CASE EXISTS
    # ----------------------------------------------------------------------
    case = CaseService.get_case(case_id)
    if not case:
        raise HTTPException(404, "Case not found")

    # Patients cannot access other people's reports
    if user.role == "patient" and case["patient_id"] != user.id:
        raise HTTPException(403, "Forbidden")

    # ----------------------------------------------------------------------
    # GET SCAN RESULTS (must contain PDF paths)
    # ----------------------------------------------------------------------
    result = ScanResultService.get_by_case(case_id)
    if not result:
        raise HTTPException(404, "Reports not generated yet")

    patient_pdf = f"/local_reports/{case_id}/patient_report.pdf"
    clinician_pdf = f"/local_reports/{case_id}/clinician_report.pdf"

    # ----------------------------------------------------------------------
    # ROLE-BASED RETURN
    # ----------------------------------------------------------------------
    if user.role == "patient":
        return {
            "patient_report": {
                "url": patient_pdf
            }
        }

    if user.role == "doctor":
        return {
            "clinician_report": {
                "url": clinician_pdf
            }
        }

    if user.role == "operator":
        return {
            "patient_report": {
                "url": patient_pdf
            }
        }

    raise HTTPException(403, "Role not allowed")
