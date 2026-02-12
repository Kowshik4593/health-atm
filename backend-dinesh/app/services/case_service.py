# app/services/case_service.py
from datetime import datetime
from app.supabase_client import supabase

def now_iso():
    return datetime.utcnow().isoformat()

class CaseService:

    @staticmethod
    def create_case(patient_id: str, storage_path: str):
        data = {
            "patient_id": patient_id,
            "storage_path": storage_path,
            "status": "uploaded",
            "updated_at": now_iso()
        }
        res = supabase.table("patient_ct_scans").insert(data).execute()
        return res.data[0]

    @staticmethod
    def update_storage_path(case_id: str, storage_path: str):
        res = supabase.table("patient_ct_scans") \
            .update({
                "storage_path": storage_path,
                "updated_at": now_iso()
            }).eq("id", case_id).execute()

        return res.data[0]

    @staticmethod
    def update_status(case_id: str, status: str):
        res = supabase.table("patient_ct_scans") \
            .update({
                "status": status,
                "updated_at": now_iso()
            }).eq("id", case_id).execute()

        return res.data[0]

    @staticmethod
    def attach_ml_outputs(case_id: str, json_path: str, clinician_pdf: str, patient_pdf: str, duration: float):
        res = supabase.table("patient_ct_scans") \
            .update({
                "json_path": json_path,
                "clinician_pdf": clinician_pdf,
                "patient_pdf": patient_pdf,
                "processing_time_seconds": duration,
                "status": "completed",
                "updated_at": now_iso()
            }).eq("id", case_id).execute()

        return res.data[0]

    @staticmethod
    def get_case(case_id: str):
        res = supabase.table("patient_ct_scans").select("*").eq("id", case_id).execute()
        return res.data[0] if res.data else None

    @staticmethod
    def get_patient_cases(patient_id: str):
        res = supabase.table("patient_ct_scans").select("*").eq("patient_id", patient_id).execute()
        return res.data

    @staticmethod
    def get_unassigned_cases():
        all_cases = supabase.table("patient_ct_scans") \
            .select("*").eq("status", "completed").execute().data

        assigned = supabase.table("doctor_assignments") \
            .select("scan_id").execute().data

        assigned_ids = {row["scan_id"] for row in assigned}

        return [c for c in all_cases if c["id"] not in assigned_ids]

    @staticmethod
    def get_assignment(assignment_id: str):
        res = supabase.table("doctor_assignments") \
                    .select("*") \
                    .eq("id", assignment_id) \
                    .execute()

        return res.data[0] if res.data else None
    @staticmethod
    def get_assignment_by_scan(scan_id: str):
        res = supabase.table("doctor_assignments") \
                      .select("*") \
                      .eq("scan_id", scan_id) \
                      .execute()
        return res.data[0] if res.data else None
    @staticmethod
    def assign_doctor(case_id: str, doctor_id: str):
    # Check if already assigned
        existing = supabase.table("doctor_assignments") \
            .select("*").eq("scan_id", case_id).execute()

        if existing.data:
            return existing.data[0]          # ★ IMPORTANT

    # Insert new assignment
        res = supabase.table("doctor_assignments").insert({
            "scan_id": case_id,
            "doctor_id": doctor_id,
            "status": "assigned"
        }).execute()

        return res.data[0]                   # ★ IMPORTANT
