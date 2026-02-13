# app/services/assignment_service.py
from datetime import datetime
from app.supabase_client import supabase

class AssignmentService:

    @staticmethod
    def accept_case(case_id: str, doctor_id: str):
        # Insert assignment
        res = supabase.table("doctor_assignments").insert({
            "scan_id": case_id,
            "doctor_id": doctor_id,
            "status": "assigned"
        }).execute()

        if not res.data:
            raise Exception("Someone else already accepted this case")

        return res.data[0]
