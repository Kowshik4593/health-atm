# backend/app/routes/doctor.py
from fastapi import APIRouter, HTTPException
from app.supabase_client import supabase
from app.audit import log
from app.notifications import notify

router = APIRouter(prefix="/doctor", tags=["doctor"])

@router.post("/accept")
def accept_case(doctor_id: str, case_id: str):
    """
    Doctor accepts a case. Ensures only one doctor can accept.
    """
    # check if case exists
    case = supabase.table("patient_ct_scans").select("*").eq("id", case_id).single().execute()
    if not case or not case.data:
        raise HTTPException(status_code=404, detail="Case not found")

    # check if already assigned
    existing = supabase.table("doctor_assignments").select("*").eq("scan_id", case_id).execute()
    if existing and existing.data:
        raise HTTPException(status_code=409, detail="Case already assigned")

    # ensure doctor_id belongs to a doctor role
    prof = supabase.table("profiles").select("role").eq("id", doctor_id).single().execute()
    role = prof.data.get("role") if prof and prof.data else None
    if role != "doctor":
        raise HTTPException(status_code=400, detail="User is not a doctor")

    # create assignment
    supabase.table("doctor_assignments").insert({
        "scan_id": case_id,
        "doctor_id": doctor_id,
        "status": "assigned"
    }).execute()

    # update case status
    supabase.table("patient_ct_scans").update({"status": "assigned", "assigned_doctor": doctor_id}).eq("id", case_id).execute()

    # create chat room automatically (if you prefer separate)
    supabase.table("chats").insert({
        "case_id": case_id,
        "doctor_id": doctor_id,
        "patient_id": case.data.get("patient_id")
    }).execute()

    # notify patient
    notify(case.data.get("patient_id"), f"Doctor has accepted your case ({case_id}). You can now chat.")
    log(doctor_id, "accepted_case", {"case_id": case_id})
    return {"success": True, "message": "Case assigned", "case_id": case_id}
