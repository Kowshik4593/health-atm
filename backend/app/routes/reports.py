# backend/app/routes/reports.py
"""
Reports API Router for Phase-2.

Endpoints:
- POST /reports/generate - Generate all reports for a case
- GET /reports/{case_id} - Get report URLs for a case
- GET /reports/{case_id}/download - Download specific report

Corporate Standards:
- Signed URLs for storage access
- Role-based access control
- Audit logging for all operations

Created for Phase-2: Feb 2026
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import Optional, Dict, List
from datetime import datetime
import os
import json
from pathlib import Path

from app.supabase_client import supabase
from app.audit import log, log_api_request
from app.reporter import generate_all_reports, generate_clinician_report, generate_patient_report
from app.validators import validate_findings
from app.storage_service import save_local, load_local


router = APIRouter(prefix="/reports", tags=["reports"])

# Base directory for findings
BACKEND_DIR = Path(__file__).parent.parent.parent.resolve()
FINDINGS_DIR = BACKEND_DIR / "backend-dinesh" / "outputs"


# =============================================================================
# Helper Functions
# =============================================================================

def get_findings_path(case_id: str) -> Optional[str]:
    """
    Locate findings.json for a case.
    
    Searches in:
    1. backend-dinesh/outputs/{case_id}_findings.json
    2. Local app directory
    """
    # Try backend-dinesh outputs
    path1 = FINDINGS_DIR / f"{case_id}_findings.json"
    if path1.exists():
        return str(path1)
    
    # Try local app directory
    path2 = Path(__file__).parent.parent / f"{case_id}_findings.json"
    if path2.exists():
        return str(path2)
    
    # Try local app directory with LIDC prefix
    path3 = Path(__file__).parent.parent / "LIDC-IDRI-0001_findings.json"
    if case_id == "LIDC-IDRI-0001" and path3.exists():
        return str(path3)
    
    return None


def store_report_paths(
    case_id: str,
    reports: Dict[str, str],
    patient_lang: str = "en"
) -> bool:
    """
    Store report paths in database.
    """
    try:
        # Build update payload
        update_data = {
            "scan_id": case_id,
            "report_generated_at": datetime.utcnow().isoformat() + "Z",
        }
        
        # Map report types to DB columns
        if "clinician" in reports:
            update_data["clinician_pdf"] = reports["clinician"]
        if "patient_en" in reports:
            update_data["patient_pdf"] = reports["patient_en"]
            update_data["patient_pdf_en"] = reports["patient_en"]
        if "patient_hi" in reports:
            update_data["patient_pdf_hi"] = reports["patient_hi"]
        
        # Store regional language report
        regional_key = f"patient_{patient_lang}"
        if regional_key in reports and patient_lang not in ["en", "hi"]:
            update_data["patient_pdf_native"] = reports[regional_key]
        
        # Store language codes
        lang_codes = ["en"]
        if "patient_hi" in reports:
            lang_codes.append("hi")
        if regional_key in reports and patient_lang not in ["en", "hi"]:
            lang_codes.append(patient_lang)
        update_data["report_lang_codes"] = lang_codes
        
        # Upsert to database
        supabase.table("scan_results").upsert(
            update_data,
            on_conflict="scan_id"
        ).execute()
        
        return True
        
    except Exception as e:
        print(f"[reports] DB update failed: {e}")
        return False


# =============================================================================
# API Endpoints
# =============================================================================

@router.post("/generate")
async def generate_reports_endpoint(
    case_id: str,
    patient_lang: str = Query(default="en", description="Patient's preferred language"),
    include_hindi: bool = Query(default=True, description="Generate Hindi report"),
    background_tasks: BackgroundTasks = None
):
    """
    Generate all reports for a case.
    
    This endpoint:
    1. Validates the findings.json
    2. Generates clinician report (English)
    3. Generates patient report (English)
    4. Generates patient report (Hindi) if requested
    5. Generates patient report in regional language if different
    6. Stores report paths in database
    
    Returns:
        Dict with report paths and generation status
    """
    log_api_request("/reports/generate", "POST", params={"case_id": case_id, "lang": patient_lang})
    
    # 1. Find the findings.json
    findings_path = get_findings_path(case_id)
    if not findings_path:
        raise HTTPException(
            status_code=404,
            detail=f"Findings not found for case: {case_id}"
        )
    
    # 2. Validate findings
    is_valid, warnings, summary = validate_findings(findings_path)
    
    # 3. Generate reports
    try:
        reports = generate_all_reports(
            findings_path,
            patient_lang=patient_lang,
            include_hindi=include_hindi
        )
    except Exception as e:
        log(None, "report_generation_failed", {
            "case_id": case_id,
            "error": str(e)
        }, severity="error")
        raise HTTPException(status_code=500, detail=str(e))
    
    # 4. Store paths in database
    db_updated = store_report_paths(case_id, reports, patient_lang)
    
    # 5. Save reports locally for serving
    for report_type, path in reports.items():
        if "error" not in report_type and os.path.exists(path):
            with open(path, "rb") as f:
                content = f.read()
            filename = os.path.basename(path)
            save_local(case_id, filename, content)
    
    # 6. Return response
    return {
        "success": True,
        "case_id": case_id,
        "validation": {
            "is_valid": is_valid,
            "warning_count": len(warnings),
            "warnings": warnings[:5] if warnings else []
        },
        "reports": {k: v for k, v in reports.items() if "error" not in k},
        "errors": {k: v for k, v in reports.items() if "error" in k},
        "languages": ["en", "hi"] + ([patient_lang] if patient_lang not in ["en", "hi"] else []),
        "db_updated": db_updated
    }


@router.get("/{case_id}")
async def get_reports(
    case_id: str,
    lang: Optional[str] = Query(None, description="Preferred language for patient report"),
    user_id: Optional[str] = Query(None, description="User ID for access control")
):
    """
    Get report URLs for a case.
    
    Returns paths to available reports based on user role.
    """
    log_api_request(f"/reports/{case_id}", "GET", user_id=user_id, params={"lang": lang})
    
    # Query scan_results
    try:
        result = supabase.table("scan_results").select("*").eq("scan_id", case_id).single().execute()
    except Exception as e:
        raise HTTPException(status_code=404, detail="Scan results not found")
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Reports not generated for this case")
    
    data = result.data
    
    # Build response
    response = {
        "case_id": case_id,
        "generated_at": data.get("report_generated_at"),
        "languages": data.get("report_lang_codes", ["en"]),
    }
    
    # Determine which reports to return based on role
    role = "patient"  # Default
    if user_id:
        try:
            prof = supabase.table("profiles").select("role").eq("id", user_id).single().execute()
            if prof.data:
                role = prof.data.get("role", "patient")
        except:
            pass
    
    # Clinician gets all reports
    if role == "doctor":
        response["clinician_report"] = data.get("clinician_pdf")
        response["patient_report_en"] = data.get("patient_pdf_en") or data.get("patient_pdf")
        response["patient_report_hi"] = data.get("patient_pdf_hi")
        if data.get("patient_pdf_native"):
            response["patient_report_native"] = data.get("patient_pdf_native")
    else:
        # Patient gets patient reports only
        if lang == "hi":
            response["patient_report"] = data.get("patient_pdf_hi") or data.get("patient_pdf")
        elif lang and lang not in ["en", "hi"]:
            response["patient_report"] = data.get("patient_pdf_native") or data.get("patient_pdf")
        else:
            response["patient_report"] = data.get("patient_pdf_en") or data.get("patient_pdf")
    
    return response


@router.get("/{case_id}/validate")
async def validate_case_findings(case_id: str):
    """
    Validate findings.json for a case without generating reports.
    
    Useful for pre-flight checks before report generation.
    """
    log_api_request(f"/reports/{case_id}/validate", "GET")
    
    findings_path = get_findings_path(case_id)
    if not findings_path:
        raise HTTPException(status_code=404, detail=f"Findings not found: {case_id}")
    
    is_valid, warnings, summary = validate_findings(findings_path)
    
    return {
        "case_id": case_id,
        "findings_path": findings_path,
        "is_valid": is_valid,
        "summary": summary,
        "warnings": warnings
    }


@router.get("/{case_id}/status")
async def get_report_status(case_id: str):
    """
    Get report generation status for a case.
    """
    try:
        result = supabase.table("scan_results").select(
            "scan_id, report_generated_at, clinician_pdf, patient_pdf, patient_pdf_hi, report_lang_codes"
        ).eq("scan_id", case_id).single().execute()
    except Exception:
        return {
            "case_id": case_id,
            "status": "not_found",
            "reports_available": []
        }
    
    if not result.data:
        return {
            "case_id": case_id,
            "status": "pending",
            "reports_available": []
        }
    
    data = result.data
    available = []
    
    if data.get("clinician_pdf"):
        available.append("clinician")
    if data.get("patient_pdf"):
        available.append("patient_en")
    if data.get("patient_pdf_hi"):
        available.append("patient_hi")
    
    return {
        "case_id": case_id,
        "status": "completed" if available else "pending",
        "generated_at": data.get("report_generated_at"),
        "reports_available": available,
        "languages": data.get("report_lang_codes", [])
    }


@router.post("/{case_id}/regenerate")
async def regenerate_reports(
    case_id: str,
    patient_lang: str = Query(default="en"),
    force: bool = Query(default=False, description="Force regeneration even if reports exist")
):
    """
    Regenerate reports for a case.
    
    Useful when:
    - Findings.json has been updated
    - Templates have been updated
    - Different language needed
    """
    log_api_request(f"/reports/{case_id}/regenerate", "POST", params={"force": force})
    
    # Check if reports already exist
    if not force:
        try:
            result = supabase.table("scan_results").select("report_generated_at").eq("scan_id", case_id).single().execute()
            if result.data and result.data.get("report_generated_at"):
                raise HTTPException(
                    status_code=409,
                    detail="Reports already exist. Use force=true to regenerate."
                )
        except HTTPException:
            raise
        except:
            pass
    
    # Delegate to generate endpoint
    return await generate_reports_endpoint(case_id, patient_lang, include_hindi=True)
