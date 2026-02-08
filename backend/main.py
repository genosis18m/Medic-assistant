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
from datetime import date, time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Literal

from database import create_db_and_tables, get_session
from models import Doctor, Specialization, PromptHistory, UserRole
from services.email_service import EMAIL_ENABLED
from services.google_calendar import CALENDAR_ENABLED
from services.slack_service import SLACK_ENABLED

print(f"\n✅ BACKEND STARTUP: Email System Enabled = {EMAIL_ENABLED}\n")


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
    doctor_id: Optional[int] = None  # Override for doctor context switching


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    session_id: str
    role: str
    suggested_actions: list[str] = []


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
                    name="Test Doctor",
                    email="doctor@clinic.com",
                    specialization=Specialization.GENERAL
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
        
        # Ensure Dr. Michael Chen has a phone number (Fix for existing DBs)
        chen = session.exec(select(Doctor).where(Doctor.name == "Dr. Michael Chen")).first()
        if chen and not chen.phone_number:
            chen.phone_number = "+919876543210"
            session.add(chen)
            session.commit()
            print("✓ Updated Dr. Michael Chen with phone number")

        # Working hours 9 AM–6 PM: set any doctor ending at 17:00 to 18:00
        six_pm = time(18, 0)
        for doc in session.exec(select(Doctor)).all():
            if doc.available_to < six_pm:
                doc.available_to = six_pm
                session.add(doc)
        session.commit()

    # ------------------------------------------------------------------
    # Startup checks for Google Calendar / Gmail credentials
    # These must never crash the app – only log clear warnings.
    # ------------------------------------------------------------------
    try:
        backend_dir = os.path.dirname(__file__)
        credentials_path = os.path.join(backend_dir, "credentials.json")
        token_path = os.path.join(backend_dir, "token.json")

        if not CALENDAR_ENABLED:
            print(
                "⚠️ Google Calendar disabled: missing GOOGLE_CLIENT_ID/GOOGLE_CLIENT_SECRET. "
                "Calendar events will not be created."
            )

        missing_files = []
        if not os.path.exists(credentials_path):
            missing_files.append("credentials.json")
        if not os.path.exists(token_path):
            missing_files.append("token.json")
        token_pickle = os.path.join(backend_dir, "token.pickle")
        if not os.path.exists(token_pickle):
            missing_files.append("token.pickle")

        if missing_files:
            print(
                "⚠️ Google Calendar/Gmail credentials missing in backend/: "
                + ", ".join(missing_files)
                + ". Integrations depending on Google APIs will be skipped, "
                "but the backend will continue running."
            )
        else:
            print("✅ Google Calendar/Gmail credential files detected (credentials.json, token.json, token.pickle)")
    except Exception as creds_e:
        print(f"⚠️ Failed to run Google credentials startup check: {creds_e}")
    
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
    allow_origins=["*"],
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
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
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
    session_data = conversation_sessions.get(session_id)

    if not session_data:
        # Try to restore from database (Persistence Fix)
        with get_session() as session:
            from sqlmodel import select
            # Get latest role from history
            statement = select(PromptHistory).where(PromptHistory.session_id == session_id).order_by(PromptHistory.created_at)
            history_entries = session.exec(statement).all()
            
            if history_entries:
                # Reconstruct history
                restored_history = []
                # Also try to restore system context - slightly tricky without storing it explicitly, 
                # but agent.py handles re-injection if history is present.
                
                for entry in history_entries:
                    restored_history.append({"role": "user", "content": entry.user_prompt})
                    restored_history.append({"role": "assistant", "content": entry.assistant_response})
                
                # Restore to memory
                session_data = {
                    "history": restored_history,
                    "role": history_entries[-1].role.value # Use role from last interaction
                }
                conversation_sessions[session_id] = session_data
                print(f"🔄 Restored session {session_id} from DB with {len(restored_history)} messages")

    if not session_data:
        session_data = {
            "history": None,
            "role": request.role
        }
        conversation_sessions[session_id] = session_data

    # Update role if changed
    if session_data["role"] != request.role:
        # Role changed, reset conversation
        session_data = {
            "history": None,
            "role": request.role
        }
    
    # Determine user context (especially for doctors)
    user_context = ""
    if request.role == "doctor":
        # Try to find doctor by email or ID
        with get_session() as session:
            from sqlmodel import select
            
            doctor = None
            
            # 1. Check for explicit doctor_id override (Context Switch)
            if request.doctor_id:
                doctor = session.get(Doctor, request.doctor_id)
            
            # 2. If no override, try email lookup
            if not doctor and request.user_email:
                doctor = session.exec(select(Doctor).where(Doctor.email == request.user_email)).first()
            
            # 3. Fallback for demo users
            if not doctor:
                if request.user_email == 'doctor12345@gmail.com':
                     # Dr. Sarah Johnson (ID 1)
                     doctor = session.exec(select(Doctor).where(Doctor.id == 1)).first()
                elif request.user_email == 'adonimohit@gmail.com':
                     # Dr. Mohit Adoni (ID 5)
                     doctor = session.exec(select(Doctor).where(Doctor.id == 5)).first()
            
            if doctor:
                user_context = f"\nSYSTEM CONTEXT: You are assisting {doctor.name} (Doctor ID: {doctor.id}). Specialization: {doctor.specialization.value}."
                if hasattr(doctor, 'phone_number') and doctor.phone_number:
                    user_context += f" Phone: {doctor.phone_number}"
    
    elif request.role == "patient":
        # Add patient context
        user_context = f"SYSTEM CONTEXT: You are assisting a patient."
        if request.user_email:
            user_context += f" Patient Email: {request.user_email}"
        if request.user_id:
            user_context += f" Patient ID: {request.user_id}"
    
    try:
        response, updated_history, suggested_actions = await chat(
            user_message=request.message,
            conversation_history=session_data["history"],
            role=request.role,
            user_context=user_context
        )
        
        # Save updated session
        session_data["history"] = updated_history
        conversation_sessions[session_id] = session_data

        try:
            print(f"💬 Chat session={session_id} role={request.role} tools_used={len([m for m in updated_history if m.get('role') == 'tool'])} suggestions={len(suggested_actions)}")
        except Exception:
            pass
        
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
            role=request.role,
            suggested_actions=suggested_actions
        )
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chat/history")
def get_chat_history(session_id: str) -> dict:
    """Get conversation history for a session."""
    if session_id in conversation_sessions:
        return {
            "history": conversation_sessions[session_id].get("history", []),
            "role": conversation_sessions[session_id].get("role", "patient")
        }
    
    # Try to fetch from DB if not in memory (optional retention)
    from sqlmodel import select
    with get_session() as session:
        statement = select(PromptHistory).where(PromptHistory.session_id == session_id).order_by(PromptHistory.created_at)
        history_entries = session.exec(statement).all()
        
        if history_entries:
            history = []
            for entry in history_entries:
                history.append({"role": "user", "content": entry.user_prompt})
                history.append({"role": "assistant", "content": entry.assistant_response})
            
            # Optionally restore to memory for faster subsequent access
            conversation_sessions[session_id] = {
                "history": history,
                "role": history_entries[-1].role.value
            }
            return {
                "history": history,
                "role": history_entries[-1].role.value
            }

        return {"history": [], "role": "patient"}


@app.get("/doctors")
def list_doctors_endpoint() -> dict:
    """List all available doctors."""
    from tools.doctors import list_doctors
    return list_doctors()


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


@app.get("/integrations/status")
def get_integrations_status() -> dict:
    """Return the current status of external integrations.

    Used by the frontend to show small UX hints when features
    like Google Calendar, Slack, or Telegram are not configured.
    """
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    google_client_id = os.getenv("GOOGLE_CLIENT_ID")
    google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    return {
        "email_enabled": bool(EMAIL_ENABLED),
        "calendar_enabled": bool(CALENDAR_ENABLED),
        "slack_enabled": bool(SLACK_ENABLED),
        "telegram_enabled": bool(telegram_token),
        "google_env_configured": bool(google_client_id and google_client_secret),
    }


@app.get("/appointments")
def list_all_appointments(
    doctor_id: Optional[int] = None,
    patient_email: Optional[str] = None,
    date_str: Optional[str] = None,
    status: Optional[str] = None
) -> dict:
    """List appointments with optional filters. Always returns { success, total, appointments }."""
    from tools.booking import list_appointments
    try:
        return list_appointments(
            patient_email=patient_email,
            doctor_id=doctor_id,
            date_str=date_str,
            status=status
        )
    except Exception as e:
        print(f"⚠️ list_appointments error: {e}")
        return {"success": False, "total": 0, "appointments": [], "error": str(e)}


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
