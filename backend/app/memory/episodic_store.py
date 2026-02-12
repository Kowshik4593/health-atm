# backend/app/memory/episodic_store.py
"""
Episodic Memory Store for HealthATM Phase-3.

Stores time-indexed episodes for each patient:
- Scan analysis events
- Chat interactions
- Report generation events
- Doctor consultations

Backed by Supabase `patient_episodes` table.
Enables longitudinal patient tracking and context for the AI agent.
"""

import json
from typing import Dict, List, Optional
from datetime import datetime

from app.supabase_client import supabase


# =============================================================================
# Episode Types
# =============================================================================

EPISODE_SCAN_ANALYSIS = "scan_analysis"
EPISODE_CHAT = "chat_interaction"
EPISODE_REPORT = "report_generated"
EPISODE_DOCTOR_CONSULT = "doctor_consultation"
EPISODE_FOLLOWUP = "followup_scheduled"


# =============================================================================
# Store Episode
# =============================================================================

def store_episode(
    patient_id: str,
    episode_type: str,
    summary: str,
    details: Optional[Dict] = None,
    scan_id: Optional[str] = None
) -> bool:
    """
    Store a new episode in the patient's episodic memory.
    
    Args:
        patient_id: Patient user ID
        episode_type: Type of episode (scan_analysis, chat, etc.)
        summary: Human-readable summary of the episode
        details: Structured episode data (findings summary, etc.)
        scan_id: Optional associated scan ID
        
    Returns:
        True if stored successfully
    """
    try:
        payload = {
            "patient_id": patient_id,
            "episode_type": episode_type,
            "summary": summary,
            "details": details or {},
            "scan_id": scan_id,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        
        supabase.table("patient_episodes").insert(payload).execute()
        return True
        
    except Exception as e:
        print(f"[episodic] ⚠️ Failed to store episode: {e}")
        return False


# =============================================================================
# Retrieve Episodes
# =============================================================================

def get_patient_episodes(
    patient_id: str,
    episode_type: Optional[str] = None,
    limit: int = 50
) -> List[Dict]:
    """
    Get all episodes for a patient, optionally filtered by type.
    
    Args:
        patient_id: Patient user ID
        episode_type: Optional filter by episode type
        limit: Max episodes to return
        
    Returns:
        List of episode dicts, newest first
    """
    try:
        query = supabase.table("patient_episodes").select("*").eq(
            "patient_id", patient_id
        )
        
        if episode_type:
            query = query.eq("episode_type", episode_type)
        
        result = query.order("created_at", desc=True).limit(limit).execute()
        return result.data or []
        
    except Exception as e:
        print(f"[episodic] ⚠️ Failed to get episodes: {e}")
        return []


def get_scan_episodes(scan_id: str) -> List[Dict]:
    """Get all episodes associated with a specific scan."""
    try:
        result = supabase.table("patient_episodes").select("*").eq(
            "scan_id", scan_id
        ).order("created_at", desc=True).execute()
        return result.data or []
    except Exception as e:
        print(f"[episodic] ⚠️ Failed to get scan episodes: {e}")
        return []


# =============================================================================
# Auto-Episode Creators
# =============================================================================

def record_scan_episode(
    patient_id: str,
    scan_id: str,
    findings: Dict
) -> bool:
    """
    Automatically create an episode from scan findings.
    Called after ML pipeline completes.
    """
    nodules = findings.get("nodules", [])
    high_risk = sum(1 for n in nodules if n.get("prob_malignant", 0) >= 0.7)
    max_size = max((n.get("long_axis_mm", 0) for n in nodules), default=0)
    
    summary = f"CT scan analysis completed: {len(nodules)} nodule(s) found"
    if high_risk > 0:
        summary += f", {high_risk} high-risk"
    if max_size > 0:
        summary += f", largest {max_size:.1f}mm"
    
    details = {
        "num_nodules": len(nodules),
        "high_risk_count": high_risk,
        "max_nodule_size_mm": max_size,
        "lung_health": findings.get("lung_health", "N/A"),
        "emphysema_score": findings.get("emphysema_score"),
        "nodule_locations": [
            n.get("location", n.get("lobe", "unspecified")) for n in nodules
        ],
        "risk_probabilities": [
            round(n.get("prob_malignant", 0), 3) for n in nodules
        ]
    }
    
    return store_episode(
        patient_id=patient_id,
        episode_type=EPISODE_SCAN_ANALYSIS,
        summary=summary,
        details=details,
        scan_id=scan_id
    )


def record_chat_episode(
    patient_id: str,
    scan_id: str,
    user_message: str,
    ai_response: str,
    tools_used: List[str] = None
) -> bool:
    """Record a chat interaction as an episode."""
    summary = f"AI chat: '{user_message[:80]}...'" if len(user_message) > 80 else f"AI chat: '{user_message}'"
    
    return store_episode(
        patient_id=patient_id,
        episode_type=EPISODE_CHAT,
        summary=summary,
        details={
            "user_message": user_message,
            "ai_response_preview": ai_response[:200],
            "tools_used": tools_used or []
        },
        scan_id=scan_id
    )


def record_report_episode(
    patient_id: str,
    scan_id: str,
    report_type: str,
    report_path: str
) -> bool:
    """Record a report generation as an episode."""
    return store_episode(
        patient_id=patient_id,
        episode_type=EPISODE_REPORT,
        summary=f"{report_type.title()} report generated",
        details={
            "report_type": report_type,
            "report_path": report_path
        },
        scan_id=scan_id
    )
