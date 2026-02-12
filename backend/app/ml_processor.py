# backend/app/ml_processor.py
"""
ML Processing Pipeline for Phase-2.

This module provides:
- Loading findings.json from ML pipeline (Dinesh's backend)
- Report generation orchestration
- Database updates
- Notification triggers

Pipeline Flow:
    1. Load findings.json from backend-dinesh/outputs/
    2. Validate findings
    3. Generate all reports (clinician + patient EN/HI)
    4. Store reports locally
    5. Update database
    6. Notify patient

Upgraded for Phase-2: Feb 2026
"""

import json
import os
import tempfile
import traceback
from pathlib import Path
from typing import Optional, Dict

from app.supabase_client import supabase
from app.notifications import notify
from app.audit import log, log_case_processing
from app.reporter import generate_all_reports
from app.validators import validate_findings
from app.storage_service import save_local, save_report_set


# =============================================================================
# Configuration
# =============================================================================

# Path to Dinesh's ML output
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
DINESH_OUTPUTS = PROJECT_ROOT / "backend-dinesh" / "outputs"


# =============================================================================
# Findings Loading
# =============================================================================

def _load_local_findings(case_id: str) -> Optional[dict]:
    """
    Load findings.json from ML pipeline output.
    
    Search order:
    1. backend-dinesh/outputs/{case_id}_findings.json
    2. backend/app/{case_id}_findings.json (for testing)
    """
    # Debug: show available directories
    print(f"[ml_processor] Looking for findings for case: {case_id}")
    print(f"[ml_processor] Dinesh outputs dir: {DINESH_OUTPUTS}")
    
    # Try Dinesh's output folder
    path1 = DINESH_OUTPUTS / f"{case_id}_findings.json"
    if path1.exists():
        print(f"[ml_processor] Found at: {path1}")
        return _load_json_file(path1)
    
    # Try local app folder (for testing)
    path2 = Path(__file__).parent / f"{case_id}_findings.json"
    if path2.exists():
        print(f"[ml_processor] Found at: {path2}")
        return _load_json_file(path2)
    
    # Try with LIDC prefix
    path3 = Path(__file__).parent / "LIDC-IDRI-0001_findings.json"
    if case_id == "LIDC-IDRI-0001" and path3.exists():
        print(f"[ml_processor] Found at: {path3}")
        return _load_json_file(path3)
    
    print(f"[ml_processor] ❌ Findings not found for: {case_id}")
    return None


def _load_json_file(path: Path) -> Optional[dict]:
    """Load and parse a JSON file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ml_processor] Failed to parse {path}: {e}")
        return None


def _get_findings_path(case_id: str) -> Optional[str]:
    """Get the path to findings.json without loading it."""
    path1 = DINESH_OUTPUTS / f"{case_id}_findings.json"
    if path1.exists():
        return str(path1)
    
    path2 = Path(__file__).parent / f"{case_id}_findings.json"
    if path2.exists():
        return str(path2)
    
    path3 = Path(__file__).parent / "LIDC-IDRI-0001_findings.json"
    if case_id == "LIDC-IDRI-0001" and path3.exists():
        return str(path3)
    
    return None


# =============================================================================
# Main Processing Function
# =============================================================================

def process_case(
    case_id: str,
    triggered_by: Optional[str] = None,
    patient_id: Optional[str] = None,
    patient_lang: str = "en"
) -> Dict:
    """
    Process a case through the full Phase-2 pipeline.
    
    Args:
        case_id: Unique case/scan identifier
        triggered_by: User ID who triggered processing
        patient_id: Patient ID for notifications
        patient_lang: Patient's preferred language
        
    Returns:
        Dict with success status and details
    """
    print(f"[ml_processor] 🚀 Starting Phase-2 processing for case: {case_id}")
    log_case_processing(case_id, "started", {"triggered_by": triggered_by})
    
    # -------------------------------------------------------------------------
    # 1. Load findings.json
    # -------------------------------------------------------------------------
    findings_path = _get_findings_path(case_id)
    if not findings_path:
        log_case_processing(case_id, "failed", {"reason": "findings.json not found"})
        return {"success": False, "reason": "findings.json missing locally"}
    
    findings = _load_local_findings(case_id)
    if findings is None:
        log_case_processing(case_id, "failed", {"reason": "failed to parse findings.json"})
        return {"success": False, "reason": "failed to parse findings.json"}
    
    print(f"[ml_processor] ✅ Loaded findings: {len(findings.get('nodules', []))} nodules")
    
    # -------------------------------------------------------------------------
    # 2. Validate findings
    # -------------------------------------------------------------------------
    is_valid, warnings, summary = validate_findings(findings)
    print(f"[ml_processor] Validation: valid={is_valid}, warnings={len(warnings)}")
    
    if warnings:
        log(None, "ml_findings_warnings", {
            "case_id": case_id,
            "warning_count": len(warnings),
            "warnings": warnings[:10]
        })
    
    # -------------------------------------------------------------------------
    # 3. Generate all reports
    # -------------------------------------------------------------------------
    try:
        reports = generate_all_reports(
            findings_path,
            patient_lang=patient_lang,
            include_hindi=True
        )
        print(f"[ml_processor] ✅ Generated reports: {list(reports.keys())}")
    except Exception as e:
        print(f"[ml_processor] ❌ Report generation error: {e}")
        traceback.print_exc()
        log_case_processing(case_id, "failed", {"reason": f"report generation failed: {str(e)}"})
        return {"success": False, "reason": "report generation failed"}
    
    # Check for errors in reports
    errors = {k: v for k, v in reports.items() if "error" in k}
    if errors:
        print(f"[ml_processor] ⚠️ Some reports failed: {errors}")
    
    # -------------------------------------------------------------------------
    # 4. Store reports locally for serving
    # -------------------------------------------------------------------------
    stored_urls = {}
    
    for report_type, path in reports.items():
        if "error" not in report_type and os.path.exists(path):
            with open(path, "rb") as f:
                content = f.read()
            filename = os.path.basename(path)
            url = save_local(case_id, filename, content)
            stored_urls[report_type] = url
            print(f"[ml_processor] Stored {report_type}: {url}")
    
    # Also store findings.json
    findings_bytes = json.dumps(findings, ensure_ascii=False, indent=2).encode("utf-8")
    save_local(case_id, "findings.json", findings_bytes)
    
    # -------------------------------------------------------------------------
    # 5. Update database
    # -------------------------------------------------------------------------
    try:
        db_payload = {
            "scan_id": case_id,
            "findings_json": findings,
            "validation_warnings": warnings[:20] if warnings else [],
            "report_generated_at": summary.get("timestamp"),
        }
        
        # Map URLs to DB columns
        if "clinician" in stored_urls:
            db_payload["clinician_pdf"] = stored_urls["clinician"]
        if "patient_en" in stored_urls:
            db_payload["patient_pdf"] = stored_urls["patient_en"]
            db_payload["patient_pdf_en"] = stored_urls["patient_en"]
        if "patient_hi" in stored_urls:
            db_payload["patient_pdf_hi"] = stored_urls["patient_hi"]
        
        supabase.table("scan_results").upsert(
            db_payload,
            on_conflict="scan_id"
        ).execute()
        
        print("[ml_processor] ✅ Database updated")
        
    except Exception as e:
        print(f"[ml_processor] ⚠️ DB update failed: {e}")
        # Continue anyway - reports are still generated
    
    # Update scan status
    try:
        supabase.table("patient_ct_scans").update({
            "status": "completed"
        }).eq("id", case_id).execute()
    except Exception:
        pass
    
    # -------------------------------------------------------------------------
    # 6. Notify patient
    # -------------------------------------------------------------------------
    try:
        if not patient_id:
            row = supabase.table("patient_ct_scans").select("patient_id").eq("id", case_id).single().execute()
            if row.data:
                patient_id = row.data.get("patient_id")
        
        if patient_id:
            notify(patient_id, f"Your scan ({case_id}) has been analyzed. Reports are ready.")
            print(f"[ml_processor] ✅ Patient notified: {patient_id}")
    except Exception as e:
        print(f"[ml_processor] ⚠️ Notification failed: {e}")
    
    # -------------------------------------------------------------------------
    # 7. Complete
    # -------------------------------------------------------------------------
    log_case_processing(case_id, "completed", {
        "nodule_count": len(findings.get("nodules", [])),
        "reports_generated": list(stored_urls.keys()),
        "validation_warnings": len(warnings)
    })
    
    print(f"[ml_processor] ✅ Case {case_id} processing complete")
    
    return {
        "success": True,
        "case_id": case_id,
        "nodules": len(findings.get("nodules", [])),
        "reports": stored_urls,
        "validation": {
            "valid": is_valid,
            "warnings": len(warnings)
        }
    }


# =============================================================================
# Batch Processing
# =============================================================================

def process_pending_cases() -> Dict:
    """
    Process all pending cases in the queue.
    
    Looks for cases with status='pending' in patient_ct_scans table.
    """
    try:
        result = supabase.table("patient_ct_scans").select("id, patient_id").eq("status", "pending").execute()
        cases = result.data or []
    except Exception as e:
        print(f"[ml_processor] Failed to fetch pending cases: {e}")
        return {"success": False, "error": str(e)}
    
    processed = []
    failed = []
    
    for case in cases:
        case_id = case.get("id")
        patient_id = case.get("patient_id")
        
        result = process_case(case_id, patient_id=patient_id)
        
        if result.get("success"):
            processed.append(case_id)
        else:
            failed.append({"case_id": case_id, "reason": result.get("reason")})
    
    return {
        "success": True,
        "processed": processed,
        "failed": failed,
        "total": len(cases)
    }


# =============================================================================
# CLI Entry Point
# =============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        case_id = sys.argv[1]
    else:
        case_id = "LIDC-IDRI-0001"
    
    print(f"🔬 Processing case: {case_id}\n")
    result = process_case(case_id)
    print(f"\n📊 Result: {json.dumps(result, indent=2)}")
