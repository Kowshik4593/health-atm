# backend/app/xai_service.py
"""
Explainability (XAI) Integration Service for Phase-2 Reports.

This module handles:
- Consuming ML-generated explainability outputs (GradCAM, saliency, overlays)
- Validating XAI asset paths
- Generating grounded, non-hallucinatory XAI descriptions
- Providing XAI references for report templates

Corporate Standards:
- No speculative language
- Every description maps to actual visual evidence
- Graceful fallback when XAI unavailable

Upgraded for Phase-2: Feb 2026
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class XAIType(Enum):
    """Types of explainability visualizations."""
    GRADCAM = "gradcam"
    SALIENCY = "saliency"
    OVERLAY = "overlay"
    MASK = "mask"
    NONE = "none"


@dataclass
class XAIAsset:
    """Represents an explainability asset."""
    type: XAIType
    path: str
    exists: bool
    description: str


# =============================================================================
# Pre-approved XAI Descriptions (No Hallucinations)
# =============================================================================

XAI_DESCRIPTIONS = {
    XAIType.GRADCAM: {
        "en": "Highlighted regions indicate areas that most influenced the AI's assessment of this nodule.",
        "hi": "हाइलाइट किए गए क्षेत्र उन स्थानों को दर्शाते हैं जिन्होंने इस नोड्यूल के AI मूल्यांकन को सबसे अधिक प्रभावित किया।",
        "te": "హైలైట్ చేయబడిన ప్రాంతాలు ఈ నోడ్యూల్ యొక్క AI అంచనాను అత్యధికంగా ప్రభావితం చేసిన ప్రాంతాలను సూచిస్తాయి.",
    },
    XAIType.SALIENCY: {
        "en": "The saliency map shows pixel-level importance for the AI's classification decision.",
        "hi": "सैलिएंसी मैप AI के वर्गीकरण निर्णय के लिए पिक्सेल-स्तरीय महत्व दिखाता है।",
        "te": "సాలియన్సీ మ్యాప్ AI వర్గీకరణ నిర్ణయానికి పిక్సెల్-స్థాయి ప్రాముఖ్యతను చూపుతుంది.",
    },
    XAIType.OVERLAY: {
        "en": "The colored overlay indicates the AI-detected nodule boundary on the CT slice.",
        "hi": "रंगीन ओवरले CT स्लाइस पर AI द्वारा पहचानी गई नोड्यूल सीमा को दर्शाता है।",
        "te": "రంగు ఓవర్‌లే CT స్లైస్‌పై AI గుర్తించిన నోడ్యూల్ సరిహద్దును సూచిస్తుంది.",
    },
    XAIType.MASK: {
        "en": "The segmentation mask shows the precise 3D volume of the detected nodule.",
        "hi": "सेगमेंटेशन मास्क पहचाने गए नोड्यूल की सटीक 3D मात्रा दिखाता है।",
        "te": "సెగ్మెంటేషన్ మాస్క్ గుర్తించబడిన నోడ్యూల్ యొక్క ఖచ్చితమైన 3D వాల్యూమ్‌ను చూపుతుంది.",
    },
    XAIType.NONE: {
        "en": "No explainability visualization is available for this finding.",
        "hi": "इस खोज के लिए कोई व्याख्यात्मक विज़ुअलाइज़ेशन उपलब्ध नहीं है।",
        "te": "ఈ కనుగొలు కోసం వివరణాత్మక విజువలైజేషన్ అందుబాటులో లేదు.",
    },
}

# Clinician-specific descriptions (more technical)
XAI_DESCRIPTIONS_CLINICIAN = {
    XAIType.GRADCAM: "GradCAM activation map showing regions contributing to malignancy probability estimation.",
    XAIType.SALIENCY: "Pixel-wise saliency map indicating gradient-based feature attribution.",
    XAIType.OVERLAY: "Segmentation overlay showing AI-detected nodule contour on axial CT slice.",
    XAIType.MASK: "3D binary segmentation mask available for volumetric analysis.",
    XAIType.NONE: "XAI visualization not generated for this nodule.",
}


# =============================================================================
# Path Validation
# =============================================================================

def validate_xai_path(path: Optional[str]) -> Tuple[bool, str]:
    """
    Validate that an XAI asset path exists.
    
    Returns:
        Tuple of (exists, resolved_path_or_error)
    """
    if not path:
        return False, "Path not provided"
    
    if path.lower() in ["not_available", "n/a", "none", ""]:
        return False, "Marked as not available"
    
    # Check absolute path
    if os.path.isabs(path):
        if os.path.exists(path):
            return True, path
        return False, f"Absolute path not found: {path}"
    
    # Check relative to common locations
    check_paths = [
        Path(path),
        Path(__file__).parent / path,
        Path(__file__).parent.parent / path,
        Path(__file__).parent.parent / "outputs" / path,
    ]
    
    for p in check_paths:
        if p.exists():
            return True, str(p.resolve())
    
    return False, f"File not found: {path}"


def get_xai_for_nodule(nodule: Dict) -> XAIAsset:
    """
    Get the best available XAI asset for a nodule.
    
    Priority: GradCAM > Saliency > Overlay > Mask
    
    Args:
        nodule: Nodule dictionary from findings.json
        
    Returns:
        XAIAsset with best available visualization
    """
    # Check in priority order
    xai_keys = [
        ("gradcam_path", XAIType.GRADCAM),
        ("saliency_path", XAIType.SALIENCY),
        ("overlay_path", XAIType.OVERLAY),
        ("mask_path", XAIType.MASK),
    ]
    
    for key, xai_type in xai_keys:
        path = nodule.get(key)
        if path:
            exists, resolved = validate_xai_path(path)
            if exists:
                return XAIAsset(
                    type=xai_type,
                    path=resolved,
                    exists=True,
                    description=XAI_DESCRIPTIONS_CLINICIAN[xai_type]
                )
    
    # No XAI available
    return XAIAsset(
        type=XAIType.NONE,
        path="",
        exists=False,
        description=XAI_DESCRIPTIONS_CLINICIAN[XAIType.NONE]
    )


def get_all_xai_for_nodule(nodule: Dict) -> List[XAIAsset]:
    """
    Get all available XAI assets for a nodule.
    
    Returns:
        List of XAIAsset objects for all available visualizations
    """
    assets = []
    
    xai_keys = [
        ("gradcam_path", XAIType.GRADCAM),
        ("saliency_path", XAIType.SALIENCY),
        ("overlay_path", XAIType.OVERLAY),
        ("mask_path", XAIType.MASK),
    ]
    
    for key, xai_type in xai_keys:
        path = nodule.get(key)
        if path:
            exists, resolved = validate_xai_path(path)
            assets.append(XAIAsset(
                type=xai_type,
                path=resolved if exists else path,
                exists=exists,
                description=XAI_DESCRIPTIONS_CLINICIAN[xai_type]
            ))
    
    return assets


# =============================================================================
# Description Generation (Grounded, No Hallucinations)
# =============================================================================

def get_xai_description(nodule: Dict, lang: str = "en", for_clinician: bool = False) -> str:
    """
    Generate a grounded XAI description for reports.
    
    Args:
        nodule: Nodule dictionary
        lang: Language code (en, hi, te)
        for_clinician: Use technical language for clinicians
        
    Returns:
        Pre-approved description string (never free-form)
    """
    xai = get_xai_for_nodule(nodule)
    
    if for_clinician:
        return XAI_DESCRIPTIONS_CLINICIAN[xai.type]
    
    descriptions = XAI_DESCRIPTIONS.get(xai.type, XAI_DESCRIPTIONS[XAIType.NONE])
    return descriptions.get(lang, descriptions["en"])


def get_xai_reference_html(nodule: Dict, base_url: str = "") -> str:
    """
    Generate HTML reference for XAI in clinician reports.
    
    Args:
        nodule: Nodule dictionary
        base_url: Base URL for serving XAI images
        
    Returns:
        HTML string with link or "Not available" text
    """
    xai = get_xai_for_nodule(nodule)
    
    if not xai.exists:
        return '<span class="xai-na">—</span>'
    
    # Generate link based on type
    type_labels = {
        XAIType.GRADCAM: "View CAM",
        XAIType.SALIENCY: "View Saliency",
        XAIType.OVERLAY: "View Overlay",
        XAIType.MASK: "View Mask",
    }
    
    label = type_labels.get(xai.type, "View")
    url = f"{base_url}/{xai.path}" if base_url else xai.path
    
    return f'<a href="{url}" class="xai-link" target="_blank">{label}</a>'


# =============================================================================
# Batch Validation for Reports
# =============================================================================

def validate_all_xai(findings: Dict) -> Dict:
    """
    Validate all XAI assets in a findings document.
    
    Returns:
        Dict with validation results and summary
    """
    nodules = findings.get("nodules", [])
    
    results = {
        "total_nodules": len(nodules),
        "with_xai": 0,
        "without_xai": 0,
        "high_risk_without_xai": 0,
        "missing_files": [],
        "available_xai": [],
    }
    
    for nodule in nodules:
        nodule_id = nodule.get("id", "unknown")
        prob = nodule.get("p_malignant") or nodule.get("prob_malignant") or 0
        
        xai = get_xai_for_nodule(nodule)
        
        if xai.exists:
            results["with_xai"] += 1
            results["available_xai"].append({
                "nodule_id": nodule_id,
                "type": xai.type.value,
                "path": xai.path
            })
        else:
            results["without_xai"] += 1
            if prob >= 0.7:
                results["high_risk_without_xai"] += 1
        
        # Check all paths for missing files
        for key in ["gradcam_path", "saliency_path", "overlay_path", "mask_path"]:
            path = nodule.get(key)
            if path and path.lower() not in ["not_available", "n/a", "none", ""]:
                exists, _ = validate_xai_path(path)
                if not exists:
                    results["missing_files"].append({
                        "nodule_id": nodule_id,
                        "field": key,
                        "path": path
                    })
    
    return results


# =============================================================================
# Report Integration Helpers
# =============================================================================

def enrich_nodules_with_xai(nodules: List[Dict], base_url: str = "") -> List[Dict]:
    """
    Add XAI metadata to nodules for template rendering.
    
    Args:
        nodules: List of nodule dicts
        base_url: Base URL for XAI assets
        
    Returns:
        Enriched nodule list with xai_* fields added
    """
    enriched = []
    
    for nodule in nodules:
        n = nodule.copy()
        xai = get_xai_for_nodule(nodule)
        
        n["xai_available"] = xai.exists
        n["xai_type"] = xai.type.value
        n["xai_path"] = xai.path if xai.exists else None
        n["xai_description"] = xai.description
        n["xai_html"] = get_xai_reference_html(nodule, base_url)
        
        enriched.append(n)
    
    return enriched


def get_xai_summary_for_report(findings: Dict, lang: str = "en") -> Dict:
    """
    Generate XAI summary section for reports.
    
    Returns:
        Dict with summary text and statistics
    """
    validation = validate_all_xai(findings)
    
    summaries = {
        "en": {
            "has_xai": f"AI explainability visualizations are available for {validation['with_xai']} of {validation['total_nodules']} detected nodules.",
            "no_xai": "No AI explainability visualizations were generated for this scan.",
            "partial_xai": f"Explainability visualizations are available for {validation['with_xai']} nodules. {validation['without_xai']} nodules do not have visualizations.",
        },
        "hi": {
            "has_xai": f"{validation['total_nodules']} में से {validation['with_xai']} नोड्यूल्स के लिए AI व्याख्यात्मकता विज़ुअलाइज़ेशन उपलब्ध हैं।",
            "no_xai": "इस स्कैन के लिए कोई AI व्याख्यात्मकता विज़ुअलाइज़ेशन उत्पन्न नहीं किया गया।",
            "partial_xai": f"{validation['with_xai']} नोड्यूल्स के लिए विज़ुअलाइज़ेशन उपलब्ध हैं। {validation['without_xai']} नोड्यूल्स में विज़ुअलाइज़ेशन नहीं हैं।",
        },
    }
    
    lang_summaries = summaries.get(lang, summaries["en"])
    
    if validation["with_xai"] == 0:
        text = lang_summaries["no_xai"]
    elif validation["without_xai"] == 0:
        text = lang_summaries["has_xai"]
    else:
        text = lang_summaries["partial_xai"]
    
    return {
        "text": text,
        "statistics": validation,
    }


# =============================================================================
# Image Embedding for PDFs (Phase-2 XAI Visual Enhancement)
# =============================================================================

def get_xai_image_base64(path: str, max_size: int = 400) -> Optional[str]:
    """
    Convert XAI image to base64 for embedding in PDFs.
    
    Args:
        path: Path to image file (PNG, JPG) or numpy mask (.npy)
        max_size: Maximum dimension for resizing
        
    Returns:
        Base64 encoded data URI string or None if failed
    """
    try:
        from PIL import Image
        import base64
        from io import BytesIO
        import numpy as np
    except ImportError:
        return None
    
    if not path or not os.path.exists(path):
        return None
    
    try:
        # Handle numpy masks
        if path.endswith('.npy'):
            mask = np.load(path)
            # Take middle slice if 3D
            if len(mask.shape) == 3:
                mid_slice = mask.shape[0] // 2
                mask = mask[mid_slice]
            # Normalize to 0-255
            mask = ((mask > 0) * 255).astype(np.uint8)
            img = Image.fromarray(mask, mode='L')
            # Apply colormap (green overlay)
            img = img.convert('RGBA')
            pixels = img.load()
            for i in range(img.width):
                for j in range(img.height):
                    if pixels[i, j][0] > 0:
                        pixels[i, j] = (0, 200, 100, 180)
                    else:
                        pixels[i, j] = (0, 0, 0, 0)
        else:
            img = Image.open(path)
        
        # Convert to RGB if needed
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize maintaining aspect ratio
        if max(img.size) > max_size:
            img.thumbnail((max_size, max_size), Image.LANCZOS)
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG', optimize=True)
        b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return f"data:image/png;base64,{b64}"
        
    except Exception as e:
        print(f"[XAI] Image encoding failed for {path}: {e}")
        return None


def get_xai_embedded_html(nodule: Dict, size: int = 120) -> str:
    """
    Generate HTML with embedded XAI image for PDF reports.
    
    Args:
        nodule: Nodule dictionary with XAI paths
        size: Display size in pixels
        
    Returns:
        HTML string with embedded image or placeholder
    """
    xai = get_xai_for_nodule(nodule)
    
    if not xai.exists:
        return '<span class="xai-na" style="color:#9ca3af;font-size:11px;">No XAI</span>'
    
    b64_data = get_xai_image_base64(xai.path, max_size=size)
    
    if not b64_data:
        return f'<span class="xai-link" style="color:#3b82f6;font-size:11px;">{xai.type.value}</span>'
    
    return f'''<img src="{b64_data}" 
        alt="{xai.type.value}" 
        style="width:{size}px;height:auto;border-radius:4px;border:1px solid #e5e7eb;"
        title="{xai.description}"/>'''


def get_xai_gallery_html(nodules: List[Dict], high_risk_only: bool = True) -> str:
    """
    Generate XAI gallery section for clinician reports.
    
    Args:
        nodules: List of nodule dicts
        high_risk_only: Only include nodules with p >= 0.7
        
    Returns:
        HTML string for XAI gallery section
    """
    gallery_items = []
    
    for n in nodules:
        prob = n.get("p_malignant") or n.get("prob_malignant") or 0
        
        # Filter based on risk
        if high_risk_only and prob < 0.7:
            continue
        
        xai = get_xai_for_nodule(n)
        if not xai.exists:
            continue
        
        b64_data = get_xai_image_base64(xai.path, max_size=300)
        if not b64_data:
            continue
        
        nodule_id = n.get("id", "?")
        risk_pct = int(prob * 100)
        
        item_html = f'''
        <div class="xai-gallery-item" style="display:inline-block;margin:8px;text-align:center;vertical-align:top;">
            <img src="{b64_data}" 
                 alt="Nodule {nodule_id} XAI" 
                 style="width:200px;height:auto;border-radius:6px;border:2px solid #ef4444;"/>
            <div style="font-size:11px;margin-top:4px;color:#374151;">
                <strong>Nodule #{nodule_id}</strong> ({risk_pct}% risk)<br/>
                <span style="color:#6b7280;">{xai.type.value.upper()}</span>
            </div>
        </div>'''
        gallery_items.append(item_html)
    
    if not gallery_items:
        return ""
    
    return f'''
    <div class="xai-gallery" style="margin:16px 0;padding:16px;background:#fef2f2;border:1px solid #fecaca;border-radius:8px;">
        <h3 style="margin:0 0 12px 0;font-size:14px;color:#991b1b;">🔍 AI Explainability Visualizations</h3>
        <p style="font-size:11px;color:#7f1d1d;margin:0 0 12px 0;">
            The following heatmaps show regions that influenced the AI's risk assessment for high-risk nodules.
        </p>
        {"".join(gallery_items)}
    </div>'''


def enrich_nodules_with_embedded_xai(nodules: List[Dict], embed_size: int = 80) -> List[Dict]:
    """
    Add embedded XAI images to nodules for template rendering.
    
    Args:
        nodules: List of nodule dicts
        embed_size: Thumbnail size for inline images
        
    Returns:
        Enriched nodule list with xai_embedded field
    """
    enriched = []
    
    for nodule in nodules:
        n = nodule.copy()
        xai = get_xai_for_nodule(nodule)
        
        n["xai_available"] = xai.exists
        n["xai_type"] = xai.type.value
        n["xai_path"] = xai.path if xai.exists else None
        n["xai_description"] = xai.description
        n["xai_embedded"] = get_xai_embedded_html(nodule, size=embed_size)
        
        enriched.append(n)
    
    return enriched


# =============================================================================
# Phase-3: LLM-Enhanced XAI Explanations
# =============================================================================

def explain_xai_with_llm(
    nodule: Dict,
    xai_type: str = "gradcam",
    for_clinician: bool = False,
    lang: str = "en"
) -> str:
    """
    Generate a natural language explanation of an XAI visualization using LLM.
    
    Falls back to pre-approved template descriptions if LLM is unavailable.
    
    Args:
        nodule: Nodule dictionary with attributes
        xai_type: Type of XAI (gradcam, saliency, overlay, mask)
        for_clinician: Use technical language
        lang: Language code
        
    Returns:
        Natural language explanation string
    """
    try:
        from app.llm_service import explain_xai_finding
        
        llm_explanation = explain_xai_finding(
            nodule=nodule,
            xai_type=xai_type,
            for_clinician=for_clinician
        )
        
        if llm_explanation:
            return llm_explanation
    except Exception as e:
        print(f"[xai] ⚠️ LLM XAI explanation unavailable: {e}")
    
    # Fallback to pre-approved descriptions
    return get_xai_description(nodule, lang=lang, for_clinician=for_clinician)


# =============================================================================
# CLI Test Entry
# =============================================================================

if __name__ == "__main__":
    import json
    import sys
    
    # Test with sample nodule
    sample_nodule = {
        "id": 1,
        "p_malignant": 0.85,
        "gradcam_path": "not_available",
        "overlay_path": "outputs/nodule_1_overlay.png",
        "mask_path": "outputs/nodule_1_mask.npy",
    }
    
    print("🔍 Testing XAI Service\n")
    
    xai = get_xai_for_nodule(sample_nodule)
    print(f"Best XAI for nodule: {xai.type.value}")
    print(f"  Path: {xai.path}")
    print(f"  Exists: {xai.exists}")
    print(f"  Description: {xai.description}")
    
    print(f"\nPatient description (EN): {get_xai_description(sample_nodule, 'en')}")
    print(f"Patient description (HI): {get_xai_description(sample_nodule, 'hi')}")
    
    print(f"\nHTML Reference: {get_xai_reference_html(sample_nodule)}")
