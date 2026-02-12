# backend/app/memory/patient_timeline.py
"""
Patient Timeline Builder for HealthATM Phase-3.

Builds a consolidated timeline of all patient interactions:
- Scan uploads and analyses
- AI chat conversations
- Report generations
- Doctor assignments and consultations

Used by the frontend PatientTimeline component and the AI agent.
"""

import json
from typing import Dict, List, Optional
from datetime import datetime

from app.supabase_client import supabase
from app.memory.episodic_store import get_patient_episodes


# =============================================================================
# Timeline Builder
# =============================================================================

def build_patient_timeline(patient_id: str, limit: int = 50) -> Dict:
    """
    Build a comprehensive timeline for a patient.
    
    Merges data from:
    - patient_episodes table (episodic memory)
    - patient_ct_scans table (scan records)
    - doctor_assignments table (consultations)
    
    Returns:
        Dict with patient info, timeline events, and summary stats
    """
    timeline_events = []
    
    # 1. Get episodic memory events
    episodes = get_patient_episodes(patient_id, limit=limit)
    for ep in episodes:
        timeline_events.append({
            "timestamp": ep.get("created_at", ""),
            "type": ep.get("episode_type", "unknown"),
            "summary": ep.get("summary", ""),
            "details": ep.get("details", {}),
            "scan_id": ep.get("scan_id"),
            "source": "episodic_memory"
        })
    
    # 2. Get scan records
    try:
        scans = supabase.table("patient_ct_scans").select(
            "id, status, created_at, file_path"
        ).eq("patient_id", patient_id).order(
            "created_at", desc=True
        ).limit(20).execute()
        
        for scan in (scans.data or []):
            # Avoid duplicates with episodes
            scan_id = scan["id"]
            already_tracked = any(
                e.get("scan_id") == scan_id and e.get("type") == "scan_analysis"
                for e in timeline_events
            )
            
            if not already_tracked:
                timeline_events.append({
                    "timestamp": scan.get("created_at", ""),
                    "type": "scan_upload",
                    "summary": f"CT scan uploaded ({scan.get('status', 'pending')})",
                    "details": {
                        "status": scan.get("status"),
                        "file_path": scan.get("file_path")
                    },
                    "scan_id": scan_id,
                    "source": "scan_records"
                })
    except Exception as e:
        print(f"[timeline] ⚠️ Failed to get scans: {e}")
    
    # 3. Get doctor assignments
    try:
        # Get scan IDs for this patient first
        scan_ids = supabase.table("patient_ct_scans").select("id").eq(
            "patient_id", patient_id
        ).execute()
        
        if scan_ids.data:
            ids = [s["id"] for s in scan_ids.data]
            # Get assignments for these scans
            for sid in ids[:10]:  # Limit
                assignments = supabase.table("doctor_assignments").select(
                    "id, doctor_id, created_at, status"
                ).eq("scan_id", sid).execute()
                
                for a in (assignments.data or []):
                    timeline_events.append({
                        "timestamp": a.get("created_at", ""),
                        "type": "doctor_assignment",
                        "summary": f"Doctor assigned to review scan",
                        "details": {
                            "assignment_id": a["id"],
                            "doctor_id": a.get("doctor_id"),
                            "status": a.get("status")
                        },
                        "scan_id": sid,
                        "source": "assignments"
                    })
    except Exception as e:
        print(f"[timeline] ⚠️ Failed to get assignments: {e}")
    
    # Sort by timestamp (newest first)
    timeline_events.sort(
        key=lambda x: x.get("timestamp", ""),
        reverse=True
    )
    
    # Build summary stats
    scan_count = sum(1 for e in timeline_events if e["type"] in ["scan_analysis", "scan_upload"])
    chat_count = sum(1 for e in timeline_events if e["type"] == "chat_interaction")
    report_count = sum(1 for e in timeline_events if e["type"] == "report_generated")
    
    return {
        "patient_id": patient_id,
        "total_events": len(timeline_events),
        "summary": {
            "total_scans": scan_count,
            "total_chats": chat_count,
            "total_reports": report_count,
            "first_visit": timeline_events[-1]["timestamp"] if timeline_events else None,
            "last_visit": timeline_events[0]["timestamp"] if timeline_events else None,
        },
        "timeline": timeline_events[:limit]
    }


# =============================================================================
# Longitudinal Analysis
# =============================================================================

def get_nodule_trends(patient_id: str) -> Dict:
    """
    Analyze nodule trends across multiple scans for a patient.
    
    Returns size and risk changes over time.
    """
    # Get all scan analysis episodes
    episodes = get_patient_episodes(
        patient_id, 
        episode_type="scan_analysis",
        limit=20
    )
    
    if len(episodes) < 2:
        return {
            "patient_id": patient_id,
            "has_trend_data": False,
            "message": "Need at least 2 scans for trend analysis",
            "scans_available": len(episodes)
        }
    
    # Build trend data
    scan_points = []
    for ep in reversed(episodes):  # Chronological order
        details = ep.get("details", {})
        scan_points.append({
            "date": ep.get("created_at", ""),
            "scan_id": ep.get("scan_id"),
            "num_nodules": details.get("num_nodules", 0),
            "high_risk_count": details.get("high_risk_count", 0),
            "max_size_mm": details.get("max_nodule_size_mm", 0),
            "locations": details.get("nodule_locations", []),
            "risk_probs": details.get("risk_probabilities", [])
        })
    
    # Calculate trends
    first = scan_points[0]
    last = scan_points[-1]
    
    trends = {
        "nodule_count_trend": last["num_nodules"] - first["num_nodules"],
        "max_size_trend_mm": round(last["max_size_mm"] - first["max_size_mm"], 2),
        "risk_trend": "increasing" if last["high_risk_count"] > first["high_risk_count"]
                      else "decreasing" if last["high_risk_count"] < first["high_risk_count"]
                      else "stable"
    }
    
    # Detect concerning growth
    if last["max_size_mm"] > first["max_size_mm"] and first["max_size_mm"] > 0:
        growth_pct = (last["max_size_mm"] - first["max_size_mm"]) / first["max_size_mm"] * 100
        trends["max_size_growth_pct"] = round(growth_pct, 1)
        trends["growth_concern"] = growth_pct > 25  # >25% growth is concerning
    
    return {
        "patient_id": patient_id,
        "has_trend_data": True,
        "num_scans": len(scan_points),
        "scan_points": scan_points,
        "trends": trends
    }
