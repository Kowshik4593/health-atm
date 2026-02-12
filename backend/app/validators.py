# backend/app/validators.py
"""
JSON Schema Validation Module for Phase-2 Report Generation.

This module provides:
- Schema-based validation of findings.json
- Graceful degradation with warnings instead of failures
- Semantic validation beyond schema (business rules)
- Audit-ready logging of validation issues

Corporate Standards:
- All validation failures logged to audit_logs
- Reports generated with warnings section if issues exist
- Never block report generation, only warn

Upgraded for Phase-2: Feb 2026
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
from datetime import datetime

try:
    from jsonschema import validate, ValidationError, Draft7Validator
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    validate = None
    ValidationError = Exception
    Draft7Validator = None

SCHEMA_PATH = Path(__file__).parent / "schema" / "findings.schema.json"


# =============================================================================
# Core Schema Validation
# =============================================================================

def load_schema() -> Dict:
    """Load the JSON schema for findings validation."""
    if not SCHEMA_PATH.exists():
        return {}
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_against_schema(data: Dict) -> List[str]:
    """
    Validate findings against JSON schema.
    
    Returns:
        List of schema validation error messages (empty if valid)
    """
    if not HAS_JSONSCHEMA:
        return ["jsonschema module not installed - schema validation skipped"]
    
    schema = load_schema()
    if not schema:
        return ["Schema file not found - validation skipped"]
    
    warnings = []
    validator = Draft7Validator(schema)
    
    for error in validator.iter_errors(data):
        path = " → ".join(str(p) for p in error.absolute_path) if error.absolute_path else "root"
        warnings.append(f"[Schema:{path}] {error.message}")
    
    return warnings


# =============================================================================
# Required Field Validation
# =============================================================================

def validate_required_fields(data: Dict) -> List[str]:
    """
    Validate business-critical required fields beyond schema.
    
    Phase-2 Requirements:
    - study_uid or study_id must exist
    - nodules array must exist (can be empty)
    - scan_metadata should exist for proper rendering
    """
    warnings = []
    
    # Study identifier
    if not data.get("study_uid") and not data.get("study_id"):
        warnings.append("[Required] Missing study identifier (study_uid or study_id)")
    
    # Nodules array
    if "nodules" not in data:
        warnings.append("[Required] Missing 'nodules' array - defaulting to empty list")
    
    # Scan metadata
    if "scan_metadata" not in data and "metadata" not in data:
        warnings.append("[Recommended] Missing scan_metadata - some report fields will show N/A")
    
    return warnings


# =============================================================================
# Nodule-Level Validation
# =============================================================================

def validate_nodule_fields(data: Dict) -> List[str]:
    """
    Validate each nodule has required fields for reporting.
    
    Required per nodule:
    - id
    - long_axis_mm or size
    - p_malignant or prob_malignant
    - type (solid/subsolid/ground-glass)
    - location or lobe
    """
    warnings = []
    nodules = data.get("nodules", [])
    
    for i, nodule in enumerate(nodules):
        nodule_id = nodule.get("id", i)
        
        # Size validation
        if not nodule.get("long_axis_mm") and not nodule.get("size"):
            warnings.append(f"[Nodule {nodule_id}] Missing size measurement")
        
        # Malignancy probability
        if nodule.get("p_malignant") is None and nodule.get("prob_malignant") is None:
            warnings.append(f"[Nodule {nodule_id}] Missing malignancy probability")
        
        # Type validation
        nodule_type = str(nodule.get("type", "")).lower()
        valid_types = ["solid", "subsolid", "ground-glass", "ground_glass", "ggo", "unknown", ""]
        if nodule_type and nodule_type not in valid_types:
            warnings.append(f"[Nodule {nodule_id}] Unknown type '{nodule_type}' - expected solid/subsolid/ground-glass")
        
        # Location validation
        if not nodule.get("location") and not nodule.get("lobe"):
            warnings.append(f"[Nodule {nodule_id}] Missing anatomical location")
    
    return warnings


# =============================================================================
# XAI/Explainability Validation
# =============================================================================

def validate_xai_paths(data: Dict) -> List[str]:
    """
    Validate explainability asset paths exist.
    
    Checks:
    - gradcam_path
    - saliency_path  
    - overlay_path
    - mask_path
    
    Only warns for high-risk nodules missing XAI.
    """
    warnings = []
    nodules = data.get("nodules", [])
    
    for nodule in nodules:
        nodule_id = nodule.get("id", "unknown")
        prob = nodule.get("p_malignant") or nodule.get("prob_malignant") or 0
        
        # Check file existence for all paths
        for key in ["gradcam_path", "saliency_path", "overlay_path", "mask_path"]:
            path_val = nodule.get(key)
            if path_val and path_val != "not_available":
                if not Path(path_val).exists():
                    warnings.append(f"[XAI:Nodule {nodule_id}] {key} file missing: {path_val}")
        
        # High-risk nodules should have XAI
        if prob >= 0.7:
            has_xai = any([
                nodule.get("gradcam_path") and nodule.get("gradcam_path") != "not_available",
                nodule.get("saliency_path") and nodule.get("saliency_path") != "not_available",
                nodule.get("overlay_path") and nodule.get("overlay_path") != "not_available",
            ])
            
            if not has_xai:
                warnings.append(
                    f"[XAI:Nodule {nodule_id}] High-risk nodule (p={prob:.2f}) missing explainability visualization"
                )
    
    return warnings


# =============================================================================
# Sanity Checks
# =============================================================================

def validate_risk_thresholds(data: Dict) -> List[str]:
    """
    Sanity check malignancy probabilities.
    
    Flags:
    - All probabilities > 0.9 (suspicious)
    - All probabilities identical (likely synthetic)
    - Negative or > 1.0 values
    - num_nodules mismatch
    """
    warnings = []
    nodules = data.get("nodules", [])
    
    # Count mismatch
    declared_count = data.get("num_nodules", 0)
    actual_count = len(nodules)
    if declared_count != actual_count:
        warnings.append(
            f"[Sanity] num_nodules mismatch: declared {declared_count} vs actual {actual_count}"
        )
    
    if not nodules:
        return warnings
    
    probs = []
    for nodule in nodules:
        prob = nodule.get("p_malignant") or nodule.get("prob_malignant")
        nodule_id = nodule.get("id", "unknown")
        
        if prob is not None:
            probs.append(prob)
            
            # Range check
            if prob < 0 or prob > 1:
                warnings.append(f"[Nodule {nodule_id}] Invalid probability {prob} - must be 0-1")
        
        # High malignancy + high uncertainty check
        uncertainty = nodule.get("uncertainty", {})
        if isinstance(uncertainty, dict):
            u_val = uncertainty.get("entropy", 0) or uncertainty.get("confidence", 0)
        else:
            u_val = uncertainty if isinstance(uncertainty, (int, float)) else 0
        
        if prob and prob > 0.8 and u_val > 0.5:
            warnings.append(
                f"[Nodule {nodule_id}] High malignancy ({prob:.2f}) but high uncertainty ({u_val:.2f}) — flagging for review"
            )
    
    if probs:
        # Suspicious patterns
        if all(p > 0.9 for p in probs) and len(probs) > 3:
            warnings.append("[Sanity] All nodules show >90% malignancy - verify ML output")
        
        if len(set(round(p, 4) for p in probs)) == 1 and len(probs) > 3:
            warnings.append("[Sanity] All nodules have identical probability - possible synthetic data")
    
    return warnings


# =============================================================================
# Main Validation Pipeline
# =============================================================================

def validate_findings(data_or_path: Union[Dict, str]) -> Tuple[bool, List[str], Dict]:
    """
    Complete validation pipeline for findings.json.
    
    Args:
        data_or_path: Either parsed findings dict or path to JSON file
        
    Returns:
        Tuple of (is_valid, list_of_warnings, summary_dict)
        - is_valid: True if no critical errors (schema passes)
        - warnings: List of all warnings/errors for report inclusion
        - summary: Structured summary for audit logging
    """
    # Load data if path provided
    if isinstance(data_or_path, str):
        try:
            with open(data_or_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            return False, [f"[Critical] Invalid JSON: {str(e)}"], {"status": "failed"}
        except FileNotFoundError:
            return False, [f"[Critical] File not found: {data_or_path}"], {"status": "failed"}
        except Exception as e:
            return False, [f"[Critical] Load error: {str(e)}"], {"status": "failed"}
    else:
        data = data_or_path
    
    all_warnings = []
    
    # 1. Schema validation
    schema_warnings = validate_against_schema(data)
    all_warnings.extend(schema_warnings)
    
    # 2. Required fields
    required_warnings = validate_required_fields(data)
    all_warnings.extend(required_warnings)
    
    # 3. Nodule fields
    nodule_warnings = validate_nodule_fields(data)
    all_warnings.extend(nodule_warnings)
    
    # 4. XAI paths
    xai_warnings = validate_xai_paths(data)
    all_warnings.extend(xai_warnings)
    
    # 5. Risk thresholds / sanity
    risk_warnings = validate_risk_thresholds(data)
    all_warnings.extend(risk_warnings)
    
    # Build summary
    summary = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "study_uid": data.get("study_uid") or data.get("study_id", "unknown"),
        "total_warnings": len(all_warnings),
        "schema_errors": len([w for w in all_warnings if w.startswith("[Schema")]),
        "required_errors": len([w for w in all_warnings if w.startswith("[Required")]),
        "nodule_errors": len([w for w in all_warnings if w.startswith("[Nodule")]),
        "xai_errors": len([w for w in all_warnings if w.startswith("[XAI")]),
        "sanity_errors": len([w for w in all_warnings if w.startswith("[Sanity")]),
        "status": "ok" if len(schema_warnings) == 0 else "failed",
        "warnings_sample": all_warnings[:20],
    }
    
    if all_warnings and summary["status"] == "ok":
        summary["status"] = "ok_with_warnings"
    
    # Consider valid if schema passed (graceful degradation)
    is_valid = len(schema_warnings) == 0
    
    return is_valid, all_warnings, summary


# =============================================================================
# Legacy API Compatibility
# =============================================================================

def validate_findings_legacy(findings_path: str) -> dict:
    """
    Legacy API for backward compatibility.
    
    Returns dict with 'errors', 'warnings', 'status' keys.
    """
    is_valid, warnings, summary = validate_findings(findings_path)
    
    # Split into errors and warnings for legacy format
    errors = [w for w in warnings if "[Schema" in w or "[Critical" in w]
    non_errors = [w for w in warnings if "[Schema" not in w and "[Critical" not in w]
    
    return {
        "errors": errors,
        "warnings": non_errors,
        "status": summary["status"]
    }


# =============================================================================
# CLI Test Entry
# =============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        test_path = sys.argv[1]
    else:
        test_path = Path(__file__).parent / "LIDC-IDRI-0001_findings.json"
    
    print(f"🔍 Validating: {test_path}\n")
    is_valid, warnings, summary = validate_findings(str(test_path))
    
    print(f"✅ Valid: {is_valid}")
    print(f"📊 Status: {summary['status']}")
    print(f"⚠️  Total Warnings: {len(warnings)}\n")
    
    if warnings:
        print("Warnings:")
        for w in warnings[:25]:
            print(f"  • {w}")
        if len(warnings) > 25:
            print(f"  ... and {len(warnings) - 25} more")
    
    print(f"\n📋 Summary: {json.dumps(summary, indent=2)}")
