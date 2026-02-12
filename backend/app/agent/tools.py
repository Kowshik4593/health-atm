# backend/app/agent/tools.py
"""
Agent Tools for the HealthATM Agentic AI Assistant.

These tools are callable by the LangGraph agent to:
- Look up patient findings from Supabase / local JSON
- Explain individual nodules
- Get scan history for a patient
- Compare scans for longitudinal tracking

Each tool is a plain function decorated with @tool for LangGraph.
"""

import json
import traceback
from typing import Optional, Dict, List
from pathlib import Path
from langchain_core.tools import tool

from app.supabase_client import supabase
from app.cache_service import get_cached_findings, cache_findings


# =============================================================================
# Tool: Lookup Findings
# =============================================================================

@tool
def lookup_findings(case_id: str) -> str:
    """Look up the CT scan analysis findings for a specific case/scan ID.
    Use this when the user asks about their scan results, nodules, or findings.
    
    Args:
        case_id: The scan or case ID to look up (e.g., 'LIDC-IDRI-0001' or a UUID)
    """
    try:
        # 1. Check disk cache
        cached = get_cached_findings(case_id)
        if cached:
            return json.dumps(cached, indent=2)
        
        # 2. Try Supabase storage (scan_results table)
        try:
            result = supabase.table("scan_results").select("*").eq(
                "scan_id", case_id
            ).single().execute()
            
            if result.data:
                findings = result.data.get("findings_json", result.data)
                if isinstance(findings, str):
                    findings = json.loads(findings)
                cache_findings(case_id, findings)
                return json.dumps(findings, indent=2)
        except Exception:
            pass
        
        # 3. Try local JSON files
        local_paths = [
            Path(__file__).parent.parent / f"{case_id}_findings.json",
            Path(__file__).parent.parent / "outputs" / f"{case_id}_findings.json",
            Path(__file__).parent.parent.parent / "backend-dinesh" / "outputs" / f"{case_id}_findings.json",
        ]
        
        for p in local_paths:
            if p.exists():
                with open(p, "r", encoding="utf-8") as f:
                    findings = json.load(f)
                cache_findings(case_id, findings)
                return json.dumps(findings, indent=2)
        
        return json.dumps({"error": f"No findings found for case {case_id}. The scan may still be processing."})
        
    except Exception as e:
        return json.dumps({"error": f"Error looking up findings: {str(e)}"})


# =============================================================================
# Tool: Explain Nodule
# =============================================================================

@tool
def explain_nodule(nodule_id: int, case_id: str) -> str:
    """Explain a specific nodule from a scan in detail.
    Use this when the user asks about a particular nodule by number.
    
    Args:
        nodule_id: The nodule number (1-indexed)
        case_id: The scan/case ID
    """
    try:
        findings_str = lookup_findings.invoke(case_id)
        findings = json.loads(findings_str)
        
        if "error" in findings:
            return findings_str
        
        nodules = findings.get("nodules", [])
        
        if nodule_id < 1 or nodule_id > len(nodules):
            return json.dumps({
                "error": f"Nodule #{nodule_id} not found. This scan has {len(nodules)} nodules."
            })
        
        n = nodules[nodule_id - 1]
        
        # Build detailed explanation
        prob = n.get("prob_malignant", n.get("p_malignant", 0))
        risk = "High" if prob >= 0.7 else "Moderate" if prob >= 0.4 else "Low"
        
        explanation = {
            "nodule_number": nodule_id,
            "size_mm": n.get("long_axis_mm", "unknown"),
            "volume_mm3": n.get("volume_mm3", "unknown"),
            "location": n.get("location", n.get("lobe", "unspecified")),
            "type": n.get("type", "unknown"),
            "malignancy_probability": f"{prob:.1%}",
            "risk_level": risk,
            "confidence": n.get("uncertainty", {}).get("confidence"),
            "needs_review": n.get("uncertainty", {}).get("needs_review", False),
            "coordinates": n.get("centroid", []),
            "xai_available": bool(n.get("gradcam_path") or n.get("xai_gradcam_path"))
        }
        
        return json.dumps(explanation, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Error explaining nodule: {str(e)}"})


# =============================================================================
# Tool: Get Scan History
# =============================================================================

@tool
def get_scan_history(patient_id: str) -> str:
    """Get the scan history for a patient, showing all their past scans.
    Use this when the user asks about their previous scans or history.
    
    Args:
        patient_id: The patient's user ID
    """
    try:
        result = supabase.table("patient_ct_scans").select(
            "id, status, created_at, file_path"
        ).eq(
            "patient_id", patient_id
        ).order(
            "created_at", desc=True
        ).limit(20).execute()
        
        scans = result.data or []
        
        if not scans:
            return json.dumps({"message": "No previous scans found for this patient.", "scans": []})
        
        # Try to get findings for each completed scan
        history = []
        for scan in scans:
            entry = {
                "scan_id": scan["id"],
                "date": scan.get("created_at", "unknown"),
                "status": scan.get("status", "unknown")
            }
            
            # If scan is completed, try to get summary
            if scan.get("status") == "completed":
                try:
                    sr = supabase.table("scan_results").select(
                        "findings_json"
                    ).eq("scan_id", scan["id"]).single().execute()
                    
                    if sr.data:
                        findings = sr.data.get("findings_json", {})
                        if isinstance(findings, str):
                            findings = json.loads(findings)
                        nodules = findings.get("nodules", [])
                        entry["num_nodules"] = len(nodules)
                        entry["high_risk_count"] = sum(
                            1 for n in nodules if n.get("prob_malignant", 0) >= 0.7
                        )
                        entry["max_nodule_size_mm"] = max(
                            (n.get("long_axis_mm", 0) for n in nodules), default=0
                        )
                except Exception:
                    pass
            
            history.append(entry)
        
        return json.dumps({"patient_id": patient_id, "total_scans": len(history), "scans": history}, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Error fetching scan history: {str(e)}"})


# =============================================================================
# Tool: Compare Scans
# =============================================================================

@tool
def compare_scans(case_id_old: str, case_id_new: str) -> str:
    """Compare two scans to detect changes in nodules over time.
    Use this when the user asks about how their scan has changed.
    
    Args:
        case_id_old: The older scan ID
        case_id_new: The newer scan ID
    """
    try:
        old_str = lookup_findings.invoke(case_id_old)
        new_str = lookup_findings.invoke(case_id_new)
        
        old = json.loads(old_str)
        new = json.loads(new_str)
        
        if "error" in old:
            return json.dumps({"error": f"Could not load old scan: {old.get('error')}"})
        if "error" in new:
            return json.dumps({"error": f"Could not load new scan: {new.get('error')}"})
        
        old_nodules = old.get("nodules", [])
        new_nodules = new.get("nodules", [])
        
        comparison = {
            "old_scan": case_id_old,
            "new_scan": case_id_new,
            "old_nodule_count": len(old_nodules),
            "new_nodule_count": len(new_nodules),
            "nodule_count_change": len(new_nodules) - len(old_nodules),
            "changes": []
        }
        
        # Simple size-based comparison (match by location/proximity)
        for i, new_n in enumerate(new_nodules):
            new_loc = new_n.get("location", new_n.get("lobe", ""))
            new_size = new_n.get("long_axis_mm", 0)
            new_prob = new_n.get("prob_malignant", 0)
            
            # Find best match in old scan by location
            best_match = None
            for old_n in old_nodules:
                old_loc = old_n.get("location", old_n.get("lobe", ""))
                if old_loc == new_loc:
                    best_match = old_n
                    break
            
            change = {
                "nodule": i + 1,
                "location": new_loc,
                "current_size_mm": new_size,
                "current_risk": new_prob
            }
            
            if best_match:
                old_size = best_match.get("long_axis_mm", 0)
                old_prob = best_match.get("prob_malignant", 0)
                
                size_change = new_size - old_size
                change["previous_size_mm"] = old_size
                change["size_change_mm"] = round(size_change, 2)
                change["size_change_pct"] = f"{(size_change / old_size * 100):.1f}%" if old_size > 0 else "N/A"
                change["risk_change"] = round(new_prob - old_prob, 3)
                change["status"] = "grew" if size_change > 0.5 else "stable" if abs(size_change) <= 0.5 else "shrunk"
            else:
                change["status"] = "new_nodule"
            
            comparison["changes"].append(change)
        
        return json.dumps(comparison, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Error comparing scans: {str(e)}"})


# =============================================================================
# Tool: Get Risk Summary
# =============================================================================

@tool
def get_risk_summary(case_id: str) -> str:
    """Get a quick risk summary for a scan — how many nodules, risk levels, recommendations.
    Use this when the user asks about their overall risk or prognosis.
    
    Args:
        case_id: The scan/case ID
    """
    try:
        findings_str = lookup_findings.invoke(case_id)
        findings = json.loads(findings_str)
        
        if "error" in findings:
            return findings_str
        
        nodules = findings.get("nodules", [])
        
        high_risk = [n for n in nodules if n.get("prob_malignant", 0) >= 0.7]
        moderate_risk = [n for n in nodules if 0.4 <= n.get("prob_malignant", 0) < 0.7]
        low_risk = [n for n in nodules if n.get("prob_malignant", 0) < 0.4]
        needs_review = [n for n in nodules if n.get("uncertainty", {}).get("needs_review")]
        
        summary = {
            "case_id": case_id,
            "total_nodules": len(nodules),
            "high_risk": len(high_risk),
            "moderate_risk": len(moderate_risk),
            "low_risk": len(low_risk),
            "needs_review": len(needs_review),
            "lung_health": findings.get("lung_health", "N/A"),
            "emphysema": findings.get("emphysema_score"),
            "overall_assessment": (
                "Urgent attention recommended" if len(high_risk) > 0
                else "Follow-up recommended" if len(moderate_risk) > 0
                else "Low risk — routine follow-up" if len(nodules) > 0
                else "No nodules detected"
            ),
            "recommendation": (
                "Immediate specialist consultation recommended." if len(high_risk) > 0
                else "Follow-up scan in 3-6 months recommended." if len(moderate_risk) > 0
                else "Routine annual screening recommended." if len(nodules) > 0
                else "Continue routine screening schedule."
            )
        }
        
        return json.dumps(summary, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Error getting risk summary: {str(e)}"})


# All tools list for agent binding
ALL_TOOLS = [lookup_findings, explain_nodule, get_scan_history, compare_scans, get_risk_summary]
