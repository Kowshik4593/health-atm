# app/services/scan_result_service.py

from app.supabase_client import supabase

class ScanResultService:

    @staticmethod
    def upsert_result(scan_id: str, storage_key: str):
        response = supabase.table("scan_results").upsert({
            "scan_id": scan_id,
            "json_path": storage_key
        }).execute()
        return response

    @staticmethod
    def get_result(scan_id):

        resp = (
            supabase.table("scan_results")
            .select("*")
            .eq("scan_id", scan_id)
            .maybe_single()
            .execute()
        )

        print("[DB] get_result resp:", resp)

        return resp.data
