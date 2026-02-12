# backend/app/audit.py
"""
Audit Logging Module for Phase-2 Compliance.

This module provides:
- Structured event logging to Supabase audit_logs table
- Validation failure tracking
- Report generation tracking
- Traceability for publication & compliance

Corporate Standards:
- All significant actions logged with timestamps
- Sensitive data properly handled
- Graceful fallback if DB unavailable

Upgraded for Phase-2: Feb 2026
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
import json
import traceback

from app.supabase_client import supabase


# =============================================================================
# Core Audit Logging
# =============================================================================

def log(
    user_id: Optional[str],
    action: str,
    details: Optional[Dict[str, Any]] = None,
    severity: str = "info"
) -> bool:
    """
    Log an action to the audit_logs table.
    
    Args:
        user_id: Optional user ID who triggered the action
        action: Action type identifier
        details: Additional context as dict
        severity: Log level - "info", "warning", "error", "critical"
        
    Returns:
        True if logged successfully, False otherwise
    """
    payload = {
        "user_id": user_id,
        "action": action,
        "details": details or {},
        "severity": severity,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    try:
        supabase.table("audit_logs").insert(payload).execute()
        return True
    except Exception as e:
        # Fallback: print to console
        print(f"[audit] ⚠️ DB log failed: {e}")
        print(f"[audit] Event: {json.dumps(payload, default=str)}")
        return False


# =============================================================================
# Specialized Logging Functions
# =============================================================================

def log_validation_failure(
    study_uid: str,
    warnings: List[str],
    is_critical: bool = False
) -> bool:
    """
    Log validation failures for a findings.json.
    
    Args:
        study_uid: Study identifier
        warnings: List of warning messages
        is_critical: Whether validation completely failed
    """
    return log(
        user_id=None,
        action="validation_failure" if is_critical else "validation_warnings",
        details={
            "study_uid": study_uid,
            "warning_count": len(warnings),
            "is_critical": is_critical,
            "warnings": warnings[:20],  # Limit stored warnings
            "full_count": len(warnings)
        },
        severity="error" if is_critical else "warning"
    )


def log_report_generated(
    study_uid: str,
    report_type: str,
    language: str,
    path: str,
    nodule_count: int = 0,
    high_risk_count: int = 0
) -> bool:
    """
    Log successful report generation.
    
    Args:
        study_uid: Study identifier
        report_type: "clinician" or "patient"
        language: Language code
        path: Output file path
        nodule_count: Total nodules in report
        high_risk_count: High risk nodules
    """
    return log(
        user_id=None,
        action="report_generated",
        details={
            "study_uid": study_uid,
            "report_type": report_type,
            "language": language,
            "output_path": path,
            "nodule_count": nodule_count,
            "high_risk_count": high_risk_count
        },
        severity="info"
    )


def log_report_failure(
    study_uid: str,
    report_type: str,
    error: str
) -> bool:
    """
    Log report generation failure.
    """
    return log(
        user_id=None,
        action="report_generation_failed",
        details={
            "study_uid": study_uid,
            "report_type": report_type,
            "error": str(error),
            "traceback": traceback.format_exc()
        },
        severity="error"
    )


def log_case_processing(
    case_id: str,
    status: str,
    details: Optional[Dict] = None
) -> bool:
    """
    Log case processing events.
    
    Status values: "started", "completed", "failed"
    """
    return log(
        user_id=None,
        action=f"case_processing_{status}",
        details={
            "case_id": case_id,
            **(details or {})
        },
        severity="info" if status != "failed" else "error"
    )


def log_translation(
    study_uid: str,
    source_lang: str,
    target_lang: str,
    success: bool
) -> bool:
    """
    Log translation events.
    """
    return log(
        user_id=None,
        action="translation_completed" if success else "translation_failed",
        details={
            "study_uid": study_uid,
            "source_lang": source_lang,
            "target_lang": target_lang
        },
        severity="info" if success else "warning"
    )


def log_xai_missing(
    study_uid: str,
    nodule_ids: List[str],
    is_high_risk: bool = False
) -> bool:
    """
    Log missing XAI assets.
    """
    return log(
        user_id=None,
        action="xai_assets_missing",
        details={
            "study_uid": study_uid,
            "affected_nodules": nodule_ids,
            "high_risk_affected": is_high_risk
        },
        severity="warning" if is_high_risk else "info"
    )


def log_api_request(
    endpoint: str,
    method: str,
    user_id: Optional[str] = None,
    params: Optional[Dict] = None
) -> bool:
    """
    Log API endpoint access.
    """
    return log(
        user_id=user_id,
        action="api_request",
        details={
            "endpoint": endpoint,
            "method": method,
            "params": params or {}
        },
        severity="info"
    )


# =============================================================================
# Audit Query Helpers (for compliance reporting)
# =============================================================================

def get_recent_events(
    action: Optional[str] = None,
    limit: int = 100
) -> List[Dict]:
    """
    Query recent audit events.
    
    Args:
        action: Filter by action type
        limit: Maximum records to return
        
    Returns:
        List of audit log entries
    """
    try:
        query = supabase.table("audit_logs").select("*")
        
        if action:
            query = query.eq("action", action)
        
        result = query.order("timestamp", desc=True).limit(limit).execute()
        return result.data or []
        
    except Exception as e:
        print(f"[audit] Query failed: {e}")
        return []


def get_events_for_study(study_uid: str) -> List[Dict]:
    """
    Get all audit events for a specific study.
    """
    try:
        result = supabase.table("audit_logs").select("*").contains(
            "details", {"study_uid": study_uid}
        ).order("timestamp", desc=True).execute()
        return result.data or []
    except Exception as e:
        print(f"[audit] Query failed: {e}")
        return []


def get_error_summary(days: int = 7) -> Dict:
    """
    Get summary of errors in the last N days.
    """
    try:
        from datetime import timedelta
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
        
        result = supabase.table("audit_logs").select("action, severity").eq(
            "severity", "error"
        ).gte("timestamp", cutoff).execute()
        
        events = result.data or []
        
        # Group by action
        summary = {}
        for event in events:
            action = event.get("action", "unknown")
            summary[action] = summary.get(action, 0) + 1
        
        return {
            "total_errors": len(events),
            "by_action": summary,
            "period_days": days
        }
        
    except Exception as e:
        print(f"[audit] Summary query failed: {e}")
        return {"error": str(e)}


# =============================================================================
# Module Test
# =============================================================================

if __name__ == "__main__":
    print("🔍 Testing Audit Module\n")
    
    # Test basic logging
    success = log(
        user_id=None,
        action="test_event",
        details={"test": True, "timestamp": datetime.utcnow().isoformat()},
        severity="info"
    )
    print(f"Basic log: {'✅' if success else '❌'}")
    
    # Test validation logging
    success = log_validation_failure(
        study_uid="TEST-001",
        warnings=["Test warning 1", "Test warning 2"],
        is_critical=False
    )
    print(f"Validation log: {'✅' if success else '❌'}")
    
    # Test report logging
    success = log_report_generated(
        study_uid="TEST-001",
        report_type="clinician",
        language="en",
        path="/tmp/test_report.pdf",
        nodule_count=5,
        high_risk_count=1
    )
    print(f"Report log: {'✅' if success else '❌'}")
    
    print("\n📊 Recent events:")
    events = get_recent_events(limit=5)
    for e in events:
        print(f"  - {e.get('action')}: {e.get('timestamp')}")
