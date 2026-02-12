# backend/app/agent/agent_core.py
"""
LangGraph Agentic AI Core for HealthATM Phase-3.

Architecture:
- StateGraph with ReAct (Reason → Act → Observe) pattern
- Groq LLM (openai/gpt-oss-120b) with tool binding
- Tools: lookup_findings, explain_nodule, get_scan_history, compare_scans, get_risk_summary
- Memory: Supabase-backed conversation persistence

Flow:
  User Message → Agent Node (LLM reasons + picks tool)
                     ↓
               Tool Node (executes tool)
                     ↓
               Agent Node (LLM observes result → responds or calls another tool)
                     ↓
               END (final response returned)
"""

import os
import json
import traceback
from typing import Dict, Optional, List, Annotated
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from app.agent.prompts import AGENT_SYSTEM_PROMPT, PATIENT_GREETING, CLINICIAN_GREETING
from app.agent.tools import ALL_TOOLS
from app.agent.memory import save_message, get_conversation_history

# Groq config
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

# =============================================================================
# LangGraph Agent Setup
# =============================================================================

LANGGRAPH_AVAILABLE = False
_compiled_agent = None

try:
    from langgraph.graph import StateGraph, MessagesState, START, END
    from langgraph.prebuilt import ToolNode, tools_condition
    from langchain_groq import ChatGroq
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    LANGGRAPH_AVAILABLE = True
except ImportError as e:
    print(f"[agent] ⚠️ LangGraph dependencies not installed: {e}")
    print("[agent] Run: pip install langgraph langchain-groq langchain-core")


def _build_agent():
    """Build and compile the LangGraph agent."""
    global _compiled_agent
    
    if not LANGGRAPH_AVAILABLE:
        return None
    
    if not GROQ_API_KEY:
        print("[agent] ⚠️ GROQ_API_KEY not set")
        return None
    
    if _compiled_agent is not None:
        return _compiled_agent
    
    try:
        # Initialize Groq LLM via LangChain
        llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model=GROQ_MODEL,
            temperature=0.3,
            max_tokens=1024,
        )
        
        # Bind tools to the LLM
        llm_with_tools = llm.bind_tools(ALL_TOOLS)
        
        # Agent node: LLM reasons and decides action
        def agent_node(state: MessagesState):
            """The agent node — calls LLM to reason about the next action."""
            # Prepend system message if not already there
            messages = state["messages"]
            if not messages or not isinstance(messages[0], SystemMessage):
                messages = [SystemMessage(content=AGENT_SYSTEM_PROMPT)] + messages
            
            response = llm_with_tools.invoke(messages)
            return {"messages": [response]}
        
        # Tool node: executes the selected tool
        tool_node = ToolNode(tools=ALL_TOOLS)
        
        # Build the graph
        graph = StateGraph(MessagesState)
        graph.add_node("agent", agent_node)
        graph.add_node("tools", tool_node)
        
        # Edges
        graph.add_edge(START, "agent")
        graph.add_conditional_edges("agent", tools_condition)
        graph.add_edge("tools", "agent")
        
        # Compile
        _compiled_agent = graph.compile()
        print("[agent] ✅ LangGraph agent compiled successfully")
        
        return _compiled_agent
        
    except Exception as e:
        print(f"[agent] ❌ Failed to build agent: {e}")
        traceback.print_exc()
        return None


# =============================================================================
# Public API
# =============================================================================

def chat_with_agent(
    user_message: str,
    patient_id: str,
    scan_id: str,
    role: str = "patient",
    include_history: bool = True
) -> Dict:
    """
    Send a message to the AI agent and get a response.
    
    Args:
        user_message: The user's message
        patient_id: Patient user ID
        scan_id: Current scan/case ID for context
        role: "patient" or "doctor"
        include_history: Whether to include past conversation
        
    Returns:
        Dict with:
        - response: The agent's text response
        - tools_used: List of tools the agent called
        - success: Boolean
    """
    agent = _build_agent()
    
    # Fallback if LangGraph isn't available
    if agent is None:
        return _fallback_response(user_message, patient_id, scan_id)
    
    try:
        # Build message list
        messages = [SystemMessage(content=AGENT_SYSTEM_PROMPT)]
        
        # Add context about current scan
        context_msg = f"[CONTEXT] Patient ID: {patient_id}. Current Scan ID: {scan_id}. User role: {role}."
        messages.append(SystemMessage(content=context_msg))
        
        # Add conversation history
        if include_history:
            history = get_conversation_history(patient_id, scan_id, limit=10)
            for msg in history:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(AIMessage(content=msg["content"]))
        
        # Add current message
        messages.append(HumanMessage(content=user_message))
        
        # Invoke agent
        result = agent.invoke({"messages": messages})
        
        # Extract response
        final_messages = result["messages"]
        
        # Get the last AI message
        response_text = ""
        tools_used = []
        
        for msg in final_messages:
            if isinstance(msg, AIMessage):
                if msg.content:
                    response_text = msg.content
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    tools_used.extend([tc["name"] for tc in msg.tool_calls])
        
        # Save to memory
        save_message(patient_id, scan_id, "user", user_message)
        save_message(patient_id, scan_id, "assistant", response_text, {
            "tools_used": tools_used
        })
        
        return {
            "response": response_text,
            "tools_used": list(set(tools_used)),
            "success": True
        }
        
    except Exception as e:
        print(f"[agent] ❌ Agent error: {e}")
        traceback.print_exc()
        return _fallback_response(user_message, patient_id, scan_id)


def _fallback_response(user_message: str, patient_id: str, scan_id: str) -> Dict:
    """
    Fallback when LangGraph is unavailable — use direct Groq API.
    """
    try:
        from app.llm_service import chat_response, SYSTEM_PROMPT_PATIENT
        
        # Get conversation history
        history = get_conversation_history(patient_id, scan_id, limit=10)
        
        # Add context
        context = f"[CONTEXT] Patient ID: {patient_id}. Scan ID: {scan_id}."
        messages = [{"role": "system", "content": context}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_message})
        
        response = chat_response(messages, SYSTEM_PROMPT_PATIENT)
        
        if response:
            save_message(patient_id, scan_id, "user", user_message)
            save_message(patient_id, scan_id, "assistant", response)
            
            return {
                "response": response,
                "tools_used": [],
                "success": True,
                "mode": "fallback"
            }
        
    except Exception as e:
        print(f"[agent] ❌ Fallback also failed: {e}")
    
    return {
        "response": "I'm sorry, I'm currently unable to process your request. Please try again later or consult your doctor directly.",
        "tools_used": [],
        "success": False,
        "mode": "error"
    }


def get_greeting(role: str = "patient") -> str:
    """Get the appropriate greeting message."""
    return PATIENT_GREETING if role == "patient" else CLINICIAN_GREETING


def agent_health_check() -> Dict:
    """Check if the agent system is operational."""
    return {
        "langgraph_available": LANGGRAPH_AVAILABLE,
        "groq_api_key_set": bool(GROQ_API_KEY),
        "model": GROQ_MODEL,
        "tools": [t.name for t in ALL_TOOLS],
        "status": "ready" if (LANGGRAPH_AVAILABLE and GROQ_API_KEY) else "unavailable"
    }
