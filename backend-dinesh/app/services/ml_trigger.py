# app/services/ml_trigger.py

import httpx
import time
import os
from pathlib import Path

from app.services.case_service import CaseService
from app.services.scan_result_service import ScanResultService
from app.services.report_generator import ReportGenerator


ML_BACKEND_URL = "http://localhost:8000/process/run"
ML_OUTPUT_DIR = Path(r"C:\Users\padal\Documents\Work\FYP-1\backend-dinesh\outputs")


class MLTriggerService:

    @staticmethod
    def trigger_ml(case_id: str, storage_path: str):
        """
        Called by /process/case endpoint.

        1. Sends case_id to backend-dinesh
        2. Returns immediately (frontend gets status="processing")
        3. ML work continues in background thread/task
        """
        import threading
        thread = threading.Thread(
            target=MLTriggerService._background_task,
            args=(case_id, storage_path),
            daemon=True
        )
        thread.start()

    # ------------------------------------------------------------------
    # INTERNAL: background ML task
    # ------------------------------------------------------------------
    @staticmethod
    def _background_task(case_id: str, storage_path: str):
        """
        This runs asynchronously:

        1. Call backend-dinesh
        2. Wait for findings.json to appear
        3. Generate PDFs
        4. Update scan_results table
        5. Mark case as completed
        """

        print(f"[MLTrigger] Starting ML background task for case {case_id}")

        # --------------------------------------------------------------
        # STEP 1 — CALL ML BACKEND (backend-dinesh)
        # --------------------------------------------------------------
        try:
            with httpx.Client(timeout=120) as client:
                resp = client.post(
                    ML_BACKEND_URL,
                    json={"case_id": case_id, "storage_path": storage_path},
                )
                resp.raise_for_status()

            print(f"[MLTrigger] ML backend accepted job for {case_id}")

        except Exception as e:
            print(f"[MLTrigger] ERROR contacting ML backend: {e}")
            CaseService.update_status(case_id, "failed")
            return

        # --------------------------------------------------------------
        # STEP 2 — WAIT FOR findings.json
        # --------------------------------------------------------------
        findings_path = MLTriggerService._wait_for_findings(case_id)

        if not findings_path:
            print(f"[MLTrigger] findings.json not found for case {case_id}")
            CaseService.update_status(case_id, "failed")
            return

        print(f"[MLTrigger] Found findings.json at: {findings_path}")

        # --------------------------------------------------------------
        # STEP 3 — GENERATE PDFs
        # --------------------------------------------------------------
        try:
            ReportGenerator.generate_reports(case_id, findings_path)
            print("[MLTrigger] Reports generated successfully")
        except Exception as e:
            print(f"[MLTrigger] PDF generation error: {e}")
            CaseService.update_status(case_id, "failed")
            return

        # --------------------------------------------------------------
        # STEP 4 — UPDATE scan_results TABLE
        # --------------------------------------------------------------
        ScanResultService.upsert_json(case_id, f"{case_id}/findings.json")
        ScanResultService.update_reports(
            case_id,
            patient_pdf="patient_report.pdf",
            clinician_pdf="clinician_report.pdf",
        )

        # --------------------------------------------------------------
        # STEP 5 — UPDATE CASE STATUS
        # --------------------------------------------------------------
        CaseService.update_status(case_id, "completed")
        print(f"[MLTrigger] Case {case_id} marked as completed")

    # ------------------------------------------------------------------
    # WAIT FOR findings.json
    # ------------------------------------------------------------------
    @staticmethod
    def _wait_for_findings(case_id: str, timeout_seconds=1800):
        """
        Poll backend-dinesh output folder for <case_id>_findings.json.
        Timeout = 30 minutes.
        """

        print(f"[MLTrigger] Waiting for findings.json for case {case_id}...")

        target_file = ML_OUTPUT_DIR / f"{case_id}_findings.json"

        waited = 0
        interval = 5  # poll every 5 seconds

        while waited <= timeout_seconds:
            if target_file.exists():
                return str(target_file)

            time.sleep(interval)
            waited += interval

        return None
