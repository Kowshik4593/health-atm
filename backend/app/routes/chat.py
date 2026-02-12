# backend/app/routes/chat.py
"""
Chat Routes for HealthATM Phase-3.

Includes:
- Original doctor-patient messaging (Phase-2)
- NEW: AI-powered chat endpoint using LangGraph agent
- NEW: Conversation history API
- NEW: Patient timeline API
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from app.supabase_client import supabase
from app.audit import log

router = APIRouter(prefix="/chat", tags=["chat"])


# =============================================================================
# Pydantic Models
# =============================================================================

class AIChatRequest(BaseModel):
    message: str
    patient_id: str
    scan_id: str
    role: str = "patient"  # "patient" or "doctor"


class AIChatResponse(BaseModel):
    response: str
    tools_used: list = []
    success: bool = True
    mode: str = "agent"


# =============================================================================
# Original Chat Endpoints (Phase-2)
# =============================================================================

@router.post("/send")
def send_message(assignment_id: str, sender_id: str, message: str, attachment_url: str | None = None):
    # ensure assignment exists
    assignment = supabase.table("doctor_assignments").select("*").eq("id", assignment_id).single().execute()
    if not assignment or not assignment.data:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # check that sender is either doctor or patient related to this case
    assn = assignment.data
    if sender_id != assn.get("doctor_id") and sender_id != (supabase.table("patient_ct_scans").select("patient_id").eq("id", assn.get("scan_id")).single().execute().data.get("patient_id")):
        raise HTTPException(status_code=403, detail="Sender not part of this chat")

    supabase.table("chat_messages").insert({
        "assignment_id": assignment_id,
        "sender_id": sender_id,
        "message": message,
        "attachment_url": attachment_url
    }).execute()
    log(sender_id, "chat_message_sent", {"assignment_id": assignment_id})
    return {"success": True}

@router.get("/messages/{assignment_id}")
def get_messages(assignment_id: str):
    msgs = supabase.table("chat_messages").select("*").eq("assignment_id", assignment_id).order("sent_at", {"ascending": True}).execute()
    return {"messages": msgs.data}


# =============================================================================
# NEW: AI Chat Endpoint (Phase-3 — LangGraph Agent)
# =============================================================================

@router.post("/ai", response_model=AIChatResponse)
def ai_chat(request: AIChatRequest):
    """
    AI-powered chat endpoint using LangGraph agent.
    
    The agent can:
    - Look up scan findings
    - Explain nodules in detail
    - Get scan history
    - Compare scans over time
    - Provide risk summaries
    
    All responses are grounded in actual data — no hallucinations.
    """
    try:
        from app.agent.agent_core import chat_with_agent
        from app.memory.episodic_store import record_chat_episode
        
        result = chat_with_agent(
            user_message=request.message,
            patient_id=request.patient_id,
            scan_id=request.scan_id,
            role=request.role,
            include_history=True
        )
        
        # Record as episodic memory
        if result.get("success"):
            record_chat_episode(
                patient_id=request.patient_id,
                scan_id=request.scan_id,
                user_message=request.message,
                ai_response=result.get("response", ""),
                tools_used=result.get("tools_used", [])
            )
        
        # Audit log
        log(request.patient_id, "ai_chat_message", {
            "scan_id": request.scan_id,
            "tools_used": result.get("tools_used", []),
            "success": result.get("success", False)
        })
        
        return AIChatResponse(
            response=result.get("response", "I'm sorry, I couldn't process your request."),
            tools_used=result.get("tools_used", []),
            success=result.get("success", False),
            mode=result.get("mode", "agent")
        )
        
    except Exception as e:
        print(f"[chat/ai] ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"AI chat error: {str(e)}")


@router.get("/ai/history/{patient_id}/{scan_id}")
def get_ai_chat_history(patient_id: str, scan_id: str):
    """Get AI chat conversation history for a patient+scan context."""
    try:
        from app.agent.memory import get_conversation_history
        
        history = get_conversation_history(patient_id, scan_id, limit=50)
        return {"messages": history, "count": len(history)}
        
    except Exception as e:
        return {"messages": [], "count": 0, "error": str(e)}


@router.get("/ai/greeting/{role}")
def get_ai_greeting(role: str = "patient"):
    """Get the AI assistant greeting message."""
    try:
        from app.agent.agent_core import get_greeting
        return {"greeting": get_greeting(role)}
    except Exception as e:
        return {"greeting": "Hello! I'm the HealthATM AI Assistant. How can I help you?"}


# =============================================================================
# NEW: Patient Timeline Endpoint (Phase-3)
# =============================================================================

@router.get("/timeline/{patient_id}")
def get_patient_timeline(patient_id: str):
    """
    Get the full patient timeline including scans, chats, and reports.
    Used by the frontend PatientTimeline component.
    """
    try:
        from app.memory.patient_timeline import build_patient_timeline
        
        timeline = build_patient_timeline(patient_id, limit=50)
        return timeline
        
    except Exception as e:
        print(f"[chat/timeline] ❌ Error: {e}")
        return {
            "patient_id": patient_id,
            "total_events": 0,
            "timeline": [],
            "error": str(e)
        }


@router.get("/trends/{patient_id}")
def get_nodule_trends(patient_id: str):
    """
    Get longitudinal nodule trends for a patient.
    Requires at least 2 completed scans.
    """
    try:
        from app.memory.patient_timeline import get_nodule_trends as _get_trends
        return _get_trends(patient_id)
    except Exception as e:
        return {
            "patient_id": patient_id,
            "has_trend_data": False,
            "error": str(e)
        }


# =============================================================================
# NEW: AI Health Check
# =============================================================================

@router.get("/ai/health")
def ai_health():
    """Check the health of the AI chat system."""
    try:
        from app.agent.agent_core import agent_health_check
        from app.llm_service import llm_health_check
        
        return {
            "agent": agent_health_check(),
            "llm": llm_health_check()
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}
