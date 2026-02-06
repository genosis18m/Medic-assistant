"""
Medical Appointment System - FastAPI Backend

Features:
- AI-powered chat with role-aware responses
- MCP tools for appointment management
- Google Calendar, Email, and Slack integrations
"""
import os
import json
from contextlib import asynccontextmanager
from datetime import date
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Literal

from database import create_db_and_tables, get_session
from models import Doctor, Specialization, PromptHistory, UserRole


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    session_id: Optional[str] = None
    role: Literal["patient", "doctor"] = "patient"
    user_email: Optional[str] = None
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    session_id: str
    role: str


class DoctorCreate(BaseModel):
    """Request model for creating a doctor."""
    name: str
    email: str
    specialization: str = "general"


class ReportRequest(BaseModel):
    """Request for generating doctor reports."""
    doctor_id: int
    report_type: Literal["daily", "weekly"] = "daily"
    date_str: Optional[str] = None
    send_slack: bool = False


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

# Store conversation histories (in-memory for now)
# In production, use Redis or database
conversation_sessions: dict[str, dict] = {}


# ============================================================================
# APP INITIALIZATION
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    create_db_and_tables()
    
    # Seed test doctors if empty
    with get_session() as session:
        from sqlmodel import select
        existing = session.exec(select(Doctor)).first()
        if not existing:
            doctors = [
                Doctor(
                    name="Dr. Sarah Johnson",
                    email="sarah@clinic.com",
                    specialization=Specialization.GENERAL
                ),
                Doctor(
                    name="Dr. Michael Chen",
                    email="michael@clinic.com",
                    specialization=Specialization.CARDIOLOGY
                ),
                Doctor(
                    name="Dr. Emily Williams",
                    email="emily@clinic.com",
                    specialization=Specialization.DERMATOLOGY
                ),
                Doctor(
                    name="Dr. James Brown",
                    email="james@clinic.com",
                    specialization=Specialization.NEUROLOGY
                ),
                Doctor(
                    name="Dr. Mohit Adoni",
                    email="adonimohit@gmail.com",
                    specialization=Specialization.GENERAL,
                    phone_number="+919425707415"
                ),
            ]
            for doc in doctors:
                session.add(doc)
            session.commit()
            print("✓ Seeded 4 doctors into database")
    
    yield


app = FastAPI(
    title="Medical Appointment System",
    description="Agentic AI with MCP - Doctor Appointment & Reporting Assistant",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default
        "http://localhost:3000",  # Alternative
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "medical-appointment-api"}


@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint with API info."""
    return {
        "message": "Medical Appointment System API",
        "docs": "/docs",
        "health": "/health",
        "version": "1.0.0"
    }


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint for the AI medical assistant.
    
    Supports both patient and doctor roles with different capabilities.
    Maintains conversation context for multi-turn interactions.
    """
    import uuid
    from agent import chat
    
    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    
    # Get existing conversation context or start new
    session_data = conversation_sessions.get(session_id, {
        "history": None,
        "role": request.role
    })
    
    # Update role if changed
    if session_data["role"] != request.role:
        # Role changed, reset conversation
        session_data = {
            "history": None,
            "role": request.role
        }
    
    try:
        response, updated_history = chat(
            user_message=request.message,
            conversation_history=session_data["history"],
            role=request.role
        )
        
        # Save updated session
        session_data["history"] = updated_history
        conversation_sessions[session_id] = session_data
        
        # Optionally save to prompt history (for analytics)
        try:
            with get_session() as db_session:
                history_entry = PromptHistory(
                    session_id=session_id,
                    role=UserRole(request.role),
                    user_prompt=request.message,
                    assistant_response=response[:2000]  # Truncate for storage
                )
                db_session.add(history_entry)
                db_session.commit()
        except Exception as e:
            print(f"⚠️ Failed to save prompt history: {e}")
        
        return ChatResponse(
            response=response,
            session_id=session_id,
            role=request.role
        )
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/doctors")
def list_doctors() -> dict:
    """List all available doctors."""
    with get_session() as session:
        from sqlmodel import select
        doctors = session.exec(select(Doctor)).all()
        return {
            "doctors": [
                {
                    "id": d.id,
                    "name": d.name,
                    "email": d.email,
                    "specialization": d.specialization.value,
                    "available_from": d.available_from.strftime("%H:%M"),
                    "available_to": d.available_to.strftime("%H:%M")
                }
                for d in doctors
            ]
        }


@app.post("/doctors")
def create_doctor(doctor: DoctorCreate) -> dict:
    """Create a new doctor."""
    with get_session() as session:
        try:
            spec = Specialization(doctor.specialization.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid specialization: {doctor.specialization}"
            )
        
        new_doctor = Doctor(
            name=doctor.name,
            email=doctor.email,
            specialization=spec
        )
        session.add(new_doctor)
        session.commit()
        session.refresh(new_doctor)
        
        return {
            "message": "Doctor created successfully",
            "doctor": {
                "id": new_doctor.id,
                "name": new_doctor.name,
                "specialization": new_doctor.specialization.value
            }
        }


@app.post("/doctor/report")
def generate_doctor_report(request: ReportRequest) -> dict:
    """
    Generate a doctor's summary report.
    
    This endpoint allows generating reports via a dashboard button
    instead of through the chat interface.
    """
    from tools.doctor_reports import generate_summary_report
    
    result = generate_summary_report(
        doctor_id=request.doctor_id,
        report_type=request.report_type,
        date_str=request.date_str or date.today().isoformat(),
        send_notification=request.send_slack
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
    
    return result


@app.get("/appointments")
def list_all_appointments(
    doctor_id: Optional[int] = None,
    date_str: Optional[str] = None,
    status: Optional[str] = None
) -> dict:
    """List appointments with optional filters."""
    from tools.booking import list_appointments
    
    return list_appointments(
        doctor_id=doctor_id,
        date_str=date_str,
        status=status
    )


@app.get("/stats")
def get_stats(
    doctor_id: Optional[int] = None,
    date_str: Optional[str] = None
) -> dict:
    """Get appointment statistics."""
    from tools.doctor_reports import get_appointment_stats
    
    result = get_appointment_stats(
        doctor_id=doctor_id,
        date_str=date_str or date.today().isoformat()
    )
    
    return result


@app.post("/notifications/test-slack")
def test_slack_notification(doctor_id: int = 1) -> dict:
    """Test Slack webhook by sending a test notification."""
    from tools.doctor_reports import send_slack_notification
    
    result = send_slack_notification(
        doctor_id=doctor_id,
        message="This is a test notification from Medical Assistant",
        include_today_summary=True
    )
    
    return result


@app.delete("/sessions/{session_id}")
def clear_session(session_id: str) -> dict:
    """Clear a conversation session."""
    if session_id in conversation_sessions:
        del conversation_sessions[session_id]
        return {"message": f"Session {session_id} cleared"}
    return {"message": "Session not found"}
