# backend/app/main.py
"""
HealthATM Backend API - Phase-3

Features:
- Patient/Doctor role-based access
- Case processing pipeline
- Report generation (clinician + patient)
- Multilingual support (EN + HI + regional)
- XAI integration
- Audit logging
- LLM-powered report narratives (Groq/openai-gpt-oss-120b)
- Agentic AI medical assistant (LangGraph)
- Episodic memory & patient timeline
- Disk cache for performance
- Case processing pipeline
- Report generation (clinician + patient)
- Multilingual support (EN + HI + regional)
- XAI integration
- Audit logging

Version: 3.0.0 (Phase-3)
Updated: Feb 2026
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from datetime import datetime

# Route imports
from app.routes import patient, doctor, cases, chat
from app.routes.debug import router as debug_router
from app.routes.reports import router as reports_router
from app.routes.upload import router as upload_router
from app.routes.process import router as process_router
from app.routes import auth, scan_results # Added from merge

# =============================================================================
# App Configuration
# =============================================================================

app = FastAPI(
    title="HealthATM Backend",
    description="AI-powered lung CT analysis platform with LLM, Agentic AI, and multilingual reporting",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# Static File Serving
# =============================================================================

# Serve generated reports
app.mount("/local_reports", StaticFiles(directory="app/local_reports"), name="local_reports")

# Serve static assets (fonts, icons)
try:
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
except Exception:
    pass  # Static folder may not exist

# =============================================================================
# Route Registration
# =============================================================================

# Core routes
app.include_router(patient.router)
app.include_router(doctor.router)
app.include_router(cases.router)
app.include_router(chat.router)

# Phase-2 routes
app.include_router(reports_router)  # /reports/* endpoints

# Phase-3 routes: Upload & AI Processing
app.include_router(upload_router)   # /upload/* endpoints
app.include_router(process_router)  # /process/* endpoints

# Merged routes (Auth & Scan Results)
app.include_router(auth.router)
app.include_router(scan_results.router)

# Debug routes (disable in production)
app.include_router(debug_router, prefix="/debug")


# =============================================================================
# Root Endpoints
# =============================================================================

@app.get("/", tags=["health"])
def root():
    """Root endpoint - API status check."""
    return {
        "status": "ok",
        "service": "HealthATM Backend",
        "version": "3.0.0",
        "phase": "Phase-3",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@app.get("/health", tags=["health"])
def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "version": "3.0.0",
        "components": {
            "api": "ok",
            "reports": "ok",
            "translation": "ok",
            "llm": "ok",
            "agent": "ok",
            "cache": "ok",
            "episodic_memory": "ok",
            "inference_service": "ok",
            "upload_service": "ok"
        },
        "features": {
            "clinician_reports": True,
            "patient_reports": True,
            "multilingual": True,
            "languages": ["en", "hi", "te"],
            "xai_integration": True,
            "llm_narratives": True,
            "agentic_ai_chat": True,
            "episodic_memory": True,
            "disk_cache": True,
            "ai_inference": True,
            "ct_scan_upload": True,
            "auto_processing": True
        }
    }


@app.get("/version", tags=["health"])
def get_version():
    """Get API version information."""
    return {
        "api_version": "3.0.0",
        "phase": "Phase-3",
        "build_date": "2026-02",
        "features": [
            "Structured Reporting Engine",
            "Multilingual Patient Reports (EN/HI)",
            "Clinician Decision Support Reports",
            "XAI/Explainability Integration",
            "JSON Schema Validation",
            "Audit Logging",
            "LLM-Powered Report Narratives (Groq)",
            "Agentic AI Medical Assistant (LangGraph)",
            "Episodic Memory & Patient Timeline",
            "Disk Cache Layer"
        ]
    }


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8050, reload=True)
