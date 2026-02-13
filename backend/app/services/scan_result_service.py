# app/services/scan_result_service.py

from app.supabase_client import supabase

class ScanResultService:

    @staticmethod
    def upsert_result(scan_id: str, storage_key: str):
        response = supabase.table("scan_results").upsert({
            "scan_id": scan_id,
            "json_path": storage_key
        }, on_conflict="scan_id").execute()
        return response

    @staticmethod
    def upsert_json(scan_id: str, json_path: str):
        """Alias for upsert_result used by ml_trigger."""
        return ScanResultService.upsert_result(scan_id, json_path)

    @staticmethod
    def update_reports(scan_id: str, patient_pdf: str = None, clinician_pdf: str = None):
        """Update the scan_results table with report PDF paths."""
        update_data = {}
        if patient_pdf:
            update_data["patient_pdf"] = patient_pdf
        if clinician_pdf:
            update_data["clinician_pdf"] = clinician_pdf

        if update_data:
            supabase.table("scan_results").update(update_data).eq("scan_id", scan_id).execute()

    @staticmethod
    def get_result(scan_id):
        resp = (
            supabase.table("scan_results")
            .select("*")
            .eq("scan_id", scan_id)
            .maybe_single()
            .execute()
        )
        return resp.data

    @staticmethod
    def get_by_case(case_id: str):
        """Alias for get_result used by reports route."""
        return ScanResultService.get_result(case_id)
