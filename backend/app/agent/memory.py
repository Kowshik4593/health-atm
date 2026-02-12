# backend/app/agent/memory.py
"""
Conversation Memory for the Agentic AI Assistant.

Uses Supabase for durable conversation storage.
Each conversation is identified by (patient_id, scan_id) pair.
"""

import json
from typing import Dict, List, Optional
from datetime import datetime

from app.supabase_client import supabase
from app.cache_service import cache_get, cache_set


# =============================================================================
# Conversation Memory (Supabase-backed)
# =============================================================================

def save_message(
    patient_id: str,
    scan_id: str,
    role: str,
    content: str,
    metadata: Optional[Dict] = None
) -> bool:
    """
    Save a chat message to Supabase ai_chat_history table.
    
    Args:
        patient_id: Patient user ID
        scan_id: Scan/case ID (conversation context)
        role: "user" or "assistant"
        content: Message content
        metadata: Optional tool calls or extra info
    """
    try:
        supabase.table("ai_chat_history").insert({
            "patient_id": patient_id,
            "scan_id": scan_id,
            "role": role,
            "content": content,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat() + "Z"
        }).execute()
        
        # Invalidate cached conversation
        cache_key = f"chat_history:{patient_id}:{scan_id}"
        from app.cache_service import cache_delete
        cache_delete(cache_key)
        
        return True
    except Exception as e:
        print(f"[memory] ⚠️ Failed to save message: {e}")
        # Table might not exist yet — graceful degradation
        return False


def get_conversation_history(
    patient_id: str,
    scan_id: str,
    limit: int = 20
) -> List[Dict[str, str]]:
    """
    Get recent conversation history for a patient+scan context.
    
    Returns list of {"role": "user"/"assistant", "content": "..."} dicts
    suitable for LLM message formatting.
    """
    # Check cache first
    cache_key = f"chat_history:{patient_id}:{scan_id}"
    cached = cache_get(cache_key)
    if cached:
        return cached
    
    try:
        result = supabase.table("ai_chat_history").select(
            "role, content"
        ).eq(
            "patient_id", patient_id
        ).eq(
            "scan_id", scan_id
        ).order(
            "created_at", desc=False
        ).limit(limit).execute()
        
        messages = [
            {"role": m["role"], "content": m["content"]}
            for m in (result.data or [])
        ]
        
        # Cache for 5 minutes
        cache_set(cache_key, messages, ttl=300)
        
        return messages
        
    except Exception as e:
        print(f"[memory] ⚠️ Failed to get history: {e}")
        return []


def clear_conversation(patient_id: str, scan_id: str) -> bool:
    """Clear conversation history for a patient+scan context."""
    try:
        supabase.table("ai_chat_history").delete().eq(
            "patient_id", patient_id
        ).eq(
            "scan_id", scan_id
        ).execute()
        return True
    except Exception as e:
        print(f"[memory] ⚠️ Failed to clear conversation: {e}")
        return False
