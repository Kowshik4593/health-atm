from fastapi import APIRouter, BackgroundTasks, HTTPException, Header
from typing import Optional
from app.ml_processor import process_case
from app.supabase_client import supabase
from app.audit import log

router = APIRouter(prefix="/cases", tags=["cases"])


# IMPORTANT: Fixed paths MUST come before parameterized paths
@router.get("/unassigned")
def get_unassigned_cases():
    """
    Get all unassigned cases (for operator dashboard).
    """
    rows = supabase.table("patient_ct_scans").select(
        "*, patient:profiles!patient_id(full_name, phone, gender)"
    ).is_("assigned_doctor", "null").order("uploaded_at", desc=True).limit(50).execute()
    return rows.data or []


@router.get("/by-patient/{pid}")
def get_cases_by_patient(pid: str):
    rows = supabase.table("patient_ct_scans").select("*").eq("patient_id", pid).order("uploaded_at", desc=True).execute()
    return rows.data


@router.get("/scan_results/{case_id}")
def get_scan_results(case_id: str):
    row = supabase.table("scan_results").select("*").eq("scan_id", case_id).single().execute()
    if not row or not row.data:
        raise HTTPException(status_code=404, detail="Scan results not found")
    return row.data


@router.get("/reports/{case_id}")
def get_report_urls(case_id: str, x_user_id: Optional[str] = Header(None, alias="x-user-id")):
    user_id = x_user_id
    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user ID header")

    scan = supabase.table("scan_results").select("*").eq("scan_id", case_id).single().execute()
    if not scan or not scan.data:
        raise HTTPException(status_code=404, detail="Scan results missing")

    prof = supabase.table("profiles").select("role").eq("id", user_id).single().execute()
    if not prof or not prof.data:
        # Fallback: check if it's the patient themselves without profile (edge case)
        # But for now, require profile.
        raise HTTPException(status_code=403, detail="User profile not found")

    role = prof.data["role"]

    urls = {}

    if role == "patient":
        urls["patient_report"] = {"url": scan.data.get("patient_pdf")}

    if role == "doctor":
        urls["clinician_report"] = {"url": scan.data.get("clinician_pdf")}
    
    # If operator/admin, maybe give both? For now stick to strict role.
    if role in ["operator", "admin"]:
         urls["patient_report"] = {"url": scan.data.get("patient_pdf")}
         urls["clinician_report"] = {"url": scan.data.get("clinician_pdf")}

    return urls


@router.post("/process/{case_id}")
def process_case_endpoint(case_id: str, background_tasks: BackgroundTasks, triggered_by: str | None = None):

    row = supabase.table("patient_ct_scans").select("*").eq("id", case_id).single().execute()
    if not row or not row.data:
        raise HTTPException(status_code=404, detail="Case not found")

    background_tasks.add_task(process_case, case_id, triggered_by, row.data.get("patient_id"))
    return {"success": True, "message": "Processing started"}


# LAST: Catch-all parameterized path
@router.get("/{case_id}")
def get_case(case_id: str):
    """
    Get a single case by ID (used for status polling from frontend).
    """
    try:
        row = supabase.table("patient_ct_scans").select("*").eq("id", case_id).single().execute()
        if not row or not row.data:
            raise HTTPException(status_code=404, detail="Case not found")
        return row.data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Case not found: {str(e)}")
