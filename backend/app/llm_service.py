# backend/app/llm_service.py
"""
LLM Integration Service for Phase-3.

Uses Groq API with openai/gpt-oss-120b for:
- Patient-friendly narrative report summaries
- Clinician differential diagnosis discussions
- XAI natural language explanations
- Agent-powered Q&A

All outputs are GROUNDED in structured findings data.
No hallucinations — system prompts enforce data-only responses.
"""

import os
import json
import traceback
from typing import Dict, Optional, List
from pathlib import Path
from dotenv import load_dotenv

# Load env
load_dotenv(Path(__file__).parent / ".env")

from app.cache_service import (
    cache_llm_response,
    get_cached_llm_response,
    make_prompt_hash
)

# Groq API setup
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

# Try to import Groq client
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("[llm] ⚠️ groq package not installed. Run: pip install groq")

_client = None

def get_groq_client():
    """Get or create Groq client (lazy init)."""
    global _client
    if not GROQ_AVAILABLE:
        return None
    if not GROQ_API_KEY:
        print("[llm] ⚠️ GROQ_API_KEY not set in .env")
        return None
    if _client is None:
        _client = Groq(api_key=GROQ_API_KEY)
    return _client


# =============================================================================
# System Prompts (Medical Safety Guardrails)
# =============================================================================

SYSTEM_PROMPT_PATIENT = """You are a medical report assistant for HealthATM, an AI-powered lung CT scan analysis platform.

RULES (STRICT):
1. ONLY use information from the provided structured data. Do NOT add any information not present.
2. Use simple, patient-friendly language. Avoid medical jargon.
3. Do NOT provide medical diagnoses or treatment advice.
4. Always recommend consulting with a doctor for any concerns.
5. Be empathetic and reassuring while remaining factual.
6. Keep responses concise (3-5 sentences for summaries).
7. If data shows high-risk findings, express this calmly without causing panic.
8. Always include the disclaimer: "This is an AI-assisted analysis and should be reviewed by a qualified medical professional."
"""

SYSTEM_PROMPT_CLINICIAN = """You are a clinical decision support assistant for HealthATM, a lung CT analysis platform.

RULES (STRICT):
1. ONLY reference findings from the provided structured data. Never fabricate findings.
2. Use precise medical terminology appropriate for radiologists/pulmonologists.
3. Reference nodule characteristics: size, location (lobe), morphology, malignancy probability.
4. Discuss differential diagnosis considerations based on imaging characteristics.
5. Reference Lung-RADS or Fleischner Society guidelines where applicable.
6. Note uncertainty metrics and recommend review where flagged.
7. Keep the tone professional and evidence-based.
8. Always state: "AI-assisted analysis — clinical correlation required."
"""

SYSTEM_PROMPT_XAI = """You are an XAI (Explainable AI) interpreter for HealthATM.

RULES (STRICT):
1. Explain ONLY what the AI model focused on based on the provided explainability data.
2. Reference the specific visualization type (GradCAM, saliency, overlay).
3. Relate highlighted regions to anatomical structures and nodule characteristics.
4. Do NOT speculate beyond what the explainability data shows.
5. Use a neutral, scientific tone.
6. Keep explanations to 2-3 sentences.
"""


# =============================================================================
# Core LLM Call
# =============================================================================

def _call_llm(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.3,
    max_tokens: int = 1024,
    use_cache: bool = True
) -> Optional[str]:
    """
    Make a grounded LLM call via Groq.
    
    Returns response text or None on failure.
    """
    # Check cache first
    if use_cache:
        prompt_hash = make_prompt_hash(user_prompt, system_prompt[:100])
        cached = get_cached_llm_response(prompt_hash)
        if cached:
            print("[llm] ✅ Cache hit")
            return cached
    
    client = get_groq_client()
    if client is None:
        return None
    
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        result = response.choices[0].message.content
        
        # Cache the response
        if use_cache and result:
            cache_llm_response(prompt_hash, result)
        
        return result
        
    except Exception as e:
        print(f"[llm] ❌ Groq API error: {e}")
        traceback.print_exc()
        return None


# =============================================================================
# Patient Narrative Summary
# =============================================================================

def generate_narrative_summary(findings: Dict, lang: str = "en") -> Optional[str]:
    """
    Generate a patient-friendly narrative summary of scan findings.
    
    Args:
        findings: Normalized findings dictionary
        lang: Language code
        
    Returns:
        Natural language summary or None
    """
    nodules = findings.get("nodules", [])
    num_nodules = len(nodules)
    
    # Build structured context
    context = {
        "study_id": findings.get("study_uid", findings.get("study_id", "unknown")),
        "total_nodules": num_nodules,
        "lung_health": findings.get("lung_health", "N/A"),
        "emphysema_score": findings.get("emphysema_score"),
        "nodules": []
    }
    
    for i, n in enumerate(nodules[:10]):  # Limit to top 10
        context["nodules"].append({
            "id": i + 1,
            "size_mm": n.get("long_axis_mm", 0),
            "location": n.get("location", n.get("lobe", "unspecified")),
            "type": n.get("type", "unknown"),
            "risk_probability": n.get("prob_malignant", 0),
            "risk_label": n.get("risk_label", "unknown"),
            "needs_review": n.get("uncertainty", {}).get("needs_review", False)
        })
    
    lang_instruction = ""
    if lang == "hi":
        lang_instruction = "\n\nRespond in Hindi (Devanagari script). Keep medical terms in English where needed."
    elif lang == "te":
        lang_instruction = "\n\nRespond in Telugu script. Keep medical terms in English where needed."
    
    prompt = f"""Generate a brief, patient-friendly summary of this CT scan analysis.

STRUCTURED DATA:
{json.dumps(context, indent=2)}

Write 3-5 sentences explaining:
1. How many nodules were found
2. The overall risk assessment
3. What the patient should do next

End with the disclaimer about AI-assisted analysis.{lang_instruction}"""

    return _call_llm(SYSTEM_PROMPT_PATIENT, prompt)


# =============================================================================
# Clinician Discussion
# =============================================================================

def generate_clinical_discussion(findings: Dict) -> Optional[str]:
    """
    Generate a clinical discussion section for clinician reports.
    
    Returns a professional differential diagnosis discussion.
    """
    nodules = findings.get("nodules", [])
    
    context = {
        "study_id": findings.get("study_uid", findings.get("study_id")),
        "total_nodules": len(nodules),
        "high_risk_nodules": sum(1 for n in nodules if n.get("prob_malignant", 0) >= 0.7),
        "lung_health": findings.get("lung_health"),
        "emphysema_score": findings.get("emphysema_score"),
        "fibrosis_score": findings.get("fibrosis_score"),
        "consolidation_score": findings.get("consolidation_score"),
        "nodules": []
    }
    
    for i, n in enumerate(nodules[:10]):
        context["nodules"].append({
            "id": i + 1,
            "size_mm": n.get("long_axis_mm", 0),
            "volume_mm3": n.get("volume_mm3", 0),
            "location": n.get("location", n.get("lobe")),
            "type": n.get("type"),
            "malignancy_probability": n.get("prob_malignant", 0),
            "confidence": n.get("uncertainty", {}).get("confidence"),
            "entropy": n.get("uncertainty", {}).get("entropy"),
            "needs_review": n.get("uncertainty", {}).get("needs_review", False)
        })
    
    prompt = f"""Generate a clinical discussion section for a radiologist review report.

STRUCTURED FINDINGS:
{json.dumps(context, indent=2)}

Include:
1. Summary of significant findings with Lung-RADS categorization where applicable
2. Differential diagnosis considerations based on nodule morphology and size
3. Recommended follow-up based on Fleischner Society guidelines
4. Note any uncertainty flags requiring additional review

Keep to 1-2 paragraphs. Be precise and evidence-based."""

    return _call_llm(SYSTEM_PROMPT_CLINICIAN, prompt, temperature=0.2)


# =============================================================================
# XAI Explanation
# =============================================================================

def explain_xai_finding(
    nodule: Dict,
    xai_type: str = "gradcam",
    for_clinician: bool = False
) -> Optional[str]:
    """
    Generate a natural language explanation of an XAI visualization.
    
    Args:
        nodule: Nodule dictionary with attributes
        xai_type: Type of XAI (gradcam, saliency, overlay)
        for_clinician: Use technical language
    """
    context = {
        "nodule_size_mm": nodule.get("long_axis_mm", 0),
        "nodule_location": nodule.get("location", nodule.get("lobe", "unspecified")),
        "nodule_type": nodule.get("type", "unknown"),
        "malignancy_probability": nodule.get("prob_malignant", 0),
        "xai_visualization_type": xai_type,
        "xai_available": bool(nodule.get(f"xai_{xai_type}_path") or nodule.get("gradcam_path"))
    }
    
    audience = "a radiologist" if for_clinician else "a patient with no medical background"
    
    prompt = f"""Explain what this {xai_type} visualization shows for the following nodule.

NODULE DATA:
{json.dumps(context, indent=2)}

Write 2-3 sentences explaining:
1. What region the AI model focused on
2. How this relates to the nodule characteristics
3. What this means for the assessment

Audience: {audience}"""

    system = SYSTEM_PROMPT_XAI if for_clinician else SYSTEM_PROMPT_PATIENT
    return _call_llm(system, prompt, temperature=0.2, max_tokens=256)


# =============================================================================
# Agent Chat Response (used by the Agentic AI)
# =============================================================================

def chat_response(
    messages: List[Dict[str, str]],
    system_prompt: str = SYSTEM_PROMPT_PATIENT,
    temperature: float = 0.4,
    max_tokens: int = 1024
) -> Optional[str]:
    """
    Generate a chat response given conversation history.
    Used by the LangGraph agent for direct responses.
    
    Args:
        messages: List of {"role": "user"/"assistant", "content": "..."} dicts
        system_prompt: System prompt to use
        
    Returns:
        Response text or None
    """
    client = get_groq_client()
    if client is None:
        return None
    
    try:
        all_messages = [{"role": "system", "content": system_prompt}] + messages
        
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=all_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"[llm] ❌ Chat response error: {e}")
        return None


# =============================================================================
# Health Check
# =============================================================================

def llm_health_check() -> Dict:
    """Check if LLM service is operational."""
    return {
        "groq_available": GROQ_AVAILABLE,
        "api_key_set": bool(GROQ_API_KEY),
        "model": GROQ_MODEL,
        "status": "ready" if (GROQ_AVAILABLE and GROQ_API_KEY) else "unavailable"
    }
