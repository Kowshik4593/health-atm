# backend/app/reporter.py
"""
Structured Report Generation Module for Phase-3.

This module provides:
- Deterministic, template-driven report generation
- LLM-powered narrative summaries (Groq/openai-gpt-oss-120b)
- Clinician reports (English only) with AI clinical discussion
- Patient reports (English + Hindi + configurable regional) with AI narratives
- XAI integration and validation warnings
- JSON-grounded content (no hallucinations)

Corporate Standards:
- Every sentence maps to JSON evidence
- LLM outputs are grounded in structured data only
- No speculative language
- No medical advice beyond screening support
- All reports include AI-assisted disclaimer

Upgraded for Phase-3: Feb 2026
"""

import json
import os
import traceback
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from datetime import datetime
import math

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML, CSS

# Import Phase-2 modules
from app.validators import validate_findings
from app.xai_service import (
    enrich_nodules_with_xai,
    get_xai_summary_for_report,
    validate_all_xai,
    enrich_nodules_with_embedded_xai,
    get_xai_gallery_html
)
from app.audit import log

# Optional numpy for mask computation
try:
    import numpy as np
except ImportError:
    np = None


# =============================================================================
# Configuration
# =============================================================================

BASE_DIR = Path(__file__).parent.resolve()
TEMPLATE_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "reports"
FONTS_DIR = BASE_DIR / "static" / "fonts"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Jinja2 environment
ENV = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=select_autoescape(['html', 'xml', 'md'])
)


# =============================================================================
# CSS Styling for PDFs
# =============================================================================

PDF_CSS = """
@page { 
  size: A4; 
  margin: 18mm 14mm 18mm 14mm; 
}

/* Font fallbacks with bundled fonts */
@font-face {
  font-family: "NotoDevanagari";
  src: url("file:///C:/Windows/Fonts/NotoSansDevanagari-Regular.ttf") format("truetype");
}

@font-face {
  font-family: "NotoTelugu";
  src: url("file:///C:/Windows/Fonts/NotoSansTelugu-Regular.ttf") format("truetype");
}

@font-face {
  font-family: "NotoLatin";
  src: url("file:///C:/Windows/Fonts/NotoSans-Regular.ttf") format("truetype");
}

body {
  font-family: "NotoTelugu", "NotoDevanagari", "NotoLatin", "Segoe UI", Arial, sans-serif;
  color: #1a1a2e;
  font-size: 12px;
  line-height: 1.5;
}

/* Print optimization */
.section, .card {
  break-inside: avoid;
}

/* Link styling for PDF */
a {
  color: #2563eb;
  text-decoration: none;
}

/* Table improvements */
table {
  border-collapse: collapse;
  width: 100%;
}

th, td {
  text-align: left;
  padding: 6px 8px;
}
"""


# =============================================================================
# Risk Label Generation (Deterministic)
# =============================================================================

def get_risk_label(prob: float, lang: str = "en") -> str:
    """
    Convert malignancy probability to patient-friendly risk label.
    
    Thresholds:
    - High: >= 0.7
    - Moderate: >= 0.4
    - Low: < 0.4
    """
    labels = {
        "en": {"high": "High", "moderate": "Moderate", "low": "Low"},
        "hi": {"high": "उच्च", "moderate": "मध्यम", "low": "कम"},
        "te": {"high": "ఎక్కువ", "moderate": "మధ్యస్థ", "low": "తక్కువ"},
    }
    
    lang_labels = labels.get(lang, labels["en"])
    
    if prob >= 0.7:
        return lang_labels["high"]
    elif prob >= 0.4:
        return lang_labels["moderate"]
    else:
        return lang_labels["low"]


def get_risk_class(prob: float) -> str:
    """Get CSS class for risk level."""
    if prob >= 0.7:
        return "high"
    elif prob >= 0.4:
        return "moderate"
    else:
        return "low"


# =============================================================================
# Data Normalization
# =============================================================================

def load_json(path: str) -> Dict:
    """Load JSON file with UTF-8 encoding."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_long_axis_from_mask(mask_path: str, spacing: Tuple = (1.0, 1.0, 1.0)) -> Optional[float]:
    """Compute long axis from 3D segmentation mask using PCA."""
    if np is None:
        return None
    try:
        p = Path(mask_path)
        if not p.exists():
            p = BASE_DIR / mask_path
        if not p.exists():
            return None
        mask = np.load(str(p))
        zs, ys, xs = np.where(mask > 0)
        if len(zs) < 2:
            return None
        coords = np.vstack([zs, ys, xs]).T.astype(float)
        coords[:, 0] *= spacing[0]
        coords[:, 1] *= spacing[1]
        coords[:, 2] *= spacing[2]
        cc = coords - coords.mean(axis=0)
        _, svals, vh = np.linalg.svd(cc, full_matrices=False)
        principal = vh[0]
        proj = cc.dot(principal)
        length = proj.max() - proj.min()
        return float(length)
    except Exception:
        return None


def normalize_fields(data: Dict, lang: str = "en") -> Dict:
    """
    Normalize and enrich findings data for template rendering.
    
    Adds:
    - Risk labels for nodules
    - XAI enrichment
    - Default values for missing fields
    - High risk count
    """
    try:
        # Study identifier
        if "study_uid" not in data:
            data["study_uid"] = data.get("study_id", "unknown")
        
        # Metadata
        meta = data.get("metadata", data.get("scan_metadata", {}))
        spacing = meta.get("spacing", [1.0, 1.0, 1.0])
        data.setdefault("spacing", spacing)
        
        # Patient info defaults
        data.setdefault("patient_name", "N/A")
        data.setdefault("patient_age", "N/A")
        data.setdefault("patient_sex", "N/A")
        data.setdefault("scan_date", "N/A")
        
        # Lung health defaults
        data.setdefault("lung_health", "")
        data.setdefault("emphysema_score", None)
        data.setdefault("fibrosis_score", None)
        data.setdefault("consolidation_score", None)
        data.setdefault("airway_wall_thickness", None)
        
        # Process nodules
        nodules = data.get("nodules", [])
        high_risk_count = 0
        
        for n in nodules:
            # Coordinate normalization
            if "centroid" not in n and "coordinates" in n:
                n["centroid"] = n["coordinates"]
            n.setdefault("centroid", [None, None, None])
            
            # Malignancy probability (support both field names)
            if "prob_malignant" not in n and "p_malignant" in n:
                n["prob_malignant"] = n["p_malignant"]
            elif "p_malignant" not in n and "prob_malignant" in n:
                n["p_malignant"] = n["prob_malignant"]
            n.setdefault("prob_malignant", 0.0)
            n.setdefault("p_malignant", n["prob_malignant"])
            
            # Other fields
            n.setdefault("volume_mm3", 0.0)
            n.setdefault("long_axis_mm", 0.0)
            n.setdefault("bbox", {})
            n.setdefault("mask_path", "")
            n.setdefault("type", "unknown")
            n.setdefault("location", n.get("lobe", "unspecified"))
            n.setdefault("lobe", n.get("location", "unspecified"))
            
            # Uncertainty handling
            uncertainty = n.get("uncertainty", {})
            if not isinstance(uncertainty, dict):
                uncertainty = {"confidence": uncertainty, "needs_review": False}
            uncertainty.setdefault("confidence", None)
            uncertainty.setdefault("entropy", None)
            uncertainty.setdefault("needs_review", False)
            n["uncertainty"] = uncertainty
            
            # Recompute long axis if suspicious
            try:
                val = float(n.get("long_axis_mm", 0.0))
                if math.isclose(val, 40.0, rel_tol=1e-6) or val <= 1.0:
                    fallback = compute_long_axis_from_mask(
                        n.get("mask_path", ""),
                        spacing=tuple(data.get("spacing", [1.0, 1.0, 1.0]))
                    )
                    if fallback:
                        n["long_axis_mm"] = round(fallback, 2)
            except Exception:
                pass
            
            # Risk labels
            prob = n.get("prob_malignant", 0)
            n["risk_label"] = get_risk_label(prob, lang)
            n["risk_class"] = get_risk_class(prob)
            
            # Count high risk
            if prob >= 0.7:
                high_risk_count += 1
        
        data["high_risk_count"] = high_risk_count
        data.setdefault("num_nodules", len(nodules))
        data.setdefault("num_candidates", data.get("num_candidates", 0))
        data.setdefault("processing_time_seconds", None)
        
        # Enrich with XAI
        data["nodules"] = enrich_nodules_with_xai(nodules)
        
        # Generation timestamp
        data["generation_time"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        return data
        
    except Exception as e:
        print(f"[reporter] normalize_fields error: {e}")
        traceback.print_exc()
        raise


# =============================================================================
# Report Generation Functions
# =============================================================================

def generate_clinician_report(findings_path: str) -> str:
    """
    Generate clinician PDF report.
    
    Features:
    - Tabular nodule summary
    - XAI references
    - Validation warnings
    - AI-assisted disclaimer
    
    Args:
        findings_path: Path to findings.json
        
    Returns:
        Path to generated PDF
    """
    try:
        # 1. Load and validate
        findings = load_json(findings_path)
        is_valid, warnings, summary = validate_findings(findings)
        
        # 2. Log validation issues
        if warnings:
            log(None, "report_validation_warnings", {
                "study_uid": findings.get("study_uid") or findings.get("study_id"),
                "report_type": "clinician",
                "warning_count": len(warnings),
                "warnings": warnings[:10]
            })
        
        # 3. Normalize data
        data = normalize_fields(findings, lang="en")
        data["validation_warnings"] = warnings
        
        # 4. Add XAI summary
        data["xai_summary"] = get_xai_summary_for_report(findings, "en")
        
        # 4b. Add embedded XAI images to nodules
        if data.get("nodules"):
            data["nodules"] = enrich_nodules_with_embedded_xai(data["nodules"], embed_size=80)
        
        # 4c. Generate XAI gallery for high-risk nodules
        data["xai_gallery"] = get_xai_gallery_html(findings.get("nodules", []), high_risk_only=True)
        
        # 4d. Phase-3: Generate LLM clinical discussion
        try:
            from app.llm_service import generate_clinical_discussion
            llm_discussion = generate_clinical_discussion(data)
            data["llm_clinical_discussion"] = llm_discussion or ""
            if llm_discussion:
                print("[reporter] 🤖 LLM clinical discussion generated")
        except Exception as llm_err:
            print(f"[reporter] ⚠️ LLM discussion unavailable: {llm_err}")
            data["llm_clinical_discussion"] = ""
        
        # 5. Render template
        template = ENV.get_template("clinician_report.md")
        rendered_html = template.render(**data)
        
        # 5b. Inject LLM discussion section if available
        if data.get("llm_clinical_discussion"):
            llm_section = f"""
            <div style="margin-top: 20px; padding: 16px; background: #f0f9ff; border-left: 4px solid #2563eb; border-radius: 8px;">
                <h3 style="color: #1e40af; margin: 0 0 8px 0; font-size: 14px;">🤖 AI-Assisted Clinical Discussion</h3>
                <p style="margin: 0; font-size: 12px; line-height: 1.6; color: #1e3a5f;">{data['llm_clinical_discussion']}</p>
                <p style="margin: 8px 0 0 0; font-size: 10px; color: #6b7280; font-style: italic;">Generated by HealthATM AI (Groq/openai-gpt-oss-120b) — Clinical correlation required.</p>
            </div>
            """
            rendered_html = rendered_html.replace("</body>", f"{llm_section}</body>")
        
        # 6. Generate PDF
        study_id = data.get("study_uid", "unknown")
        out_path = (OUTPUT_DIR / f"clinician_{study_id}.pdf").resolve()
        
        HTML(string=rendered_html).write_pdf(
            str(out_path),
            stylesheets=[CSS(string=PDF_CSS)]
        )
        
        print(f"[reporter] ✅ Clinician PDF: {out_path}")
        
        # 7. Audit log
        log(None, "report_generated", {
            "study_uid": study_id,
            "report_type": "clinician",
            "path": str(out_path),
            "nodule_count": len(data.get("nodules", [])),
            "high_risk_count": data.get("high_risk_count", 0),
            "llm_enhanced": bool(data.get("llm_clinical_discussion"))
        })
        
        return str(out_path)
        
    except Exception as e:
        print(f"[reporter] ❌ generate_clinician_report error: {e}")
        traceback.print_exc()
        raise


def generate_patient_report(findings_path: str, lang: str = "en") -> str:
    """
    Generate patient-friendly PDF report.
    
    Features:
    - Simple vocabulary
    - Qualitative risk labels (not probabilities)
    - Clear next-step guidance
    - Pre-translated templates
    
    Args:
        findings_path: Path to findings.json
        lang: Language code ("en", "hi", etc.)
        
    Returns:
        Path to generated PDF
    """
    try:
        # 1. Load and validate
        findings = load_json(findings_path)
        is_valid, warnings, summary = validate_findings(findings)
        
        # 2. Normalize data with language-specific labels
        data = normalize_fields(findings, lang=lang)
        data["validation_warnings"] = []  # Don't show technical warnings to patients
        
        # 3. Select template based on language
        template_name = f"patient_report_{lang}.md"
        
        # Fallback to English if template doesn't exist
        template_path = TEMPLATE_DIR / template_name
        if not template_path.exists():
            print(f"[reporter] Template {template_name} not found, falling back to English")
            template_name = "patient_report_en.md"
            lang = "en"
        
        # 3b. Add simplified XAI gallery for patient (high-risk only)
        data["xai_gallery"] = get_xai_gallery_html(findings.get("nodules", []), high_risk_only=True)
        
        # 3c. Phase-3: Generate LLM patient narrative
        try:
            from app.llm_service import generate_narrative_summary
            llm_narrative = generate_narrative_summary(data, lang=lang)
            data["llm_narrative"] = llm_narrative or ""
            if llm_narrative:
                print(f"[reporter] 🤖 LLM patient narrative generated ({lang})")
        except Exception as llm_err:
            print(f"[reporter] ⚠️ LLM narrative unavailable: {llm_err}")
            data["llm_narrative"] = ""
        
        template = ENV.get_template(template_name)
        rendered_html = template.render(**data)
        
        # 3d. Inject LLM narrative section if available
        if data.get("llm_narrative"):
            llm_section = f"""
            <div style="margin-top: 20px; padding: 16px; background: #f0fdf4; border-left: 4px solid #16a34a; border-radius: 8px;">
                <h3 style="color: #166534; margin: 0 0 8px 0; font-size: 14px;">🤖 AI Summary — What Your Scan Shows</h3>
                <p style="margin: 0; font-size: 12px; line-height: 1.6; color: #14532d;">{data['llm_narrative']}</p>
                <p style="margin: 8px 0 0 0; font-size: 10px; color: #6b7280; font-style: italic;">This summary is generated by AI and should be reviewed with your doctor.</p>
            </div>
            """
            rendered_html = rendered_html.replace("</body>", f"{llm_section}</body>")
        
        # 4. Generate PDF
        study_id = data.get("study_uid", "unknown")
        out_path = (OUTPUT_DIR / f"patient_{lang}_{study_id}.pdf").resolve()
        
        HTML(string=rendered_html).write_pdf(
            str(out_path),
            stylesheets=[CSS(string=PDF_CSS)]
        )
        
        print(f"[reporter] ✅ Patient PDF ({lang}): {out_path}")
        
        # 5. Audit log
        log(None, "report_generated", {
            "study_uid": study_id,
            "report_type": "patient",
            "language": lang,
            "path": str(out_path),
            "nodule_count": len(data.get("nodules", [])),
            "high_risk_count": data.get("high_risk_count", 0),
            "llm_enhanced": bool(data.get("llm_narrative"))
        })
        
        return str(out_path)
        
    except Exception as e:
        print(f"[reporter] ❌ generate_patient_report error: {e}")
        traceback.print_exc()
        raise


def generate_all_reports(
    findings_path: str,
    patient_lang: str = "en",
    include_hindi: bool = True
) -> Dict[str, str]:
    """
    Generate all required reports for a case.
    
    Phase-2 Requirements:
    - Clinician report (English)
    - Patient report (English) - mandatory
    - Patient report (Hindi) - mandatory
    - Patient report (regional) - if different from EN/HI
    
    Args:
        findings_path: Path to findings.json
        patient_lang: Patient's preferred language
        include_hindi: Whether to generate Hindi report (default True)
        
    Returns:
        Dict mapping report type to file path
    """
    reports = {}
    
    # 1. Clinician report (English only)
    try:
        reports["clinician"] = generate_clinician_report(findings_path)
    except Exception as e:
        print(f"[reporter] Failed to generate clinician report: {e}")
        reports["clinician_error"] = str(e)
    
    # 2. Patient report - English (mandatory)
    try:
        reports["patient_en"] = generate_patient_report(findings_path, "en")
    except Exception as e:
        print(f"[reporter] Failed to generate English patient report: {e}")
        reports["patient_en_error"] = str(e)
    
    # 3. Patient report - Hindi (mandatory)
    if include_hindi:
        try:
            reports["patient_hi"] = generate_patient_report(findings_path, "hi")
        except Exception as e:
            print(f"[reporter] Failed to generate Hindi patient report: {e}")
            reports["patient_hi_error"] = str(e)
    
    # 4. Patient report - Regional (if different)
    if patient_lang and patient_lang.lower() not in ["en", "hi", "english", "hindi"]:
        try:
            reports[f"patient_{patient_lang}"] = generate_patient_report(
                findings_path, patient_lang.lower()
            )
        except Exception as e:
            print(f"[reporter] Failed to generate {patient_lang} patient report: {e}")
            reports[f"patient_{patient_lang}_error"] = str(e)
    
    return reports


# =============================================================================
# Legacy API Compatibility
# =============================================================================

def generate_patient_summary(
    findings_json: str,
    patient_lang: Optional[str] = None,
    top_k: int = 10
) -> str:
    """
    Legacy API wrapper for backward compatibility.
    
    Delegates to new generate_patient_report function.
    """
    lang = "en"
    if patient_lang:
        lang = patient_lang.lower()
    
    return generate_patient_report(findings_json, lang)


# =============================================================================
# CLI Entry Point
# =============================================================================

if __name__ == "__main__":
    import sys
    
    # Default sample file
    sample_json = BASE_DIR / "LIDC-IDRI-0001_findings.json"
    
    if len(sys.argv) > 1:
        sample_json = Path(sys.argv[1])
    
    if not sample_json.exists():
        print(f"❌ File not found: {sample_json}")
        sys.exit(1)
    
    print(f"📄 Processing: {sample_json}\n")
    
    # Generate all reports
    reports = generate_all_reports(
        str(sample_json),
        patient_lang="hi",
        include_hindi=True
    )
    
    print("\n" + "=" * 50)
    print("📊 Generated Reports:")
    for report_type, path in reports.items():
        if "error" in report_type:
            print(f"  ❌ {report_type}: {path}")
        else:
            print(f"  ✅ {report_type}: {path}")
