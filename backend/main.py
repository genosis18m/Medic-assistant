"""
Medical Appointment System - FastAPI Backend
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional

from database import create_db_and_tables, get_session
from models import Doctor, Specialization


# Pydantic models for request/response
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    session_id: str


class DoctorCreate(BaseModel):
    """Request model for creating a doctor."""
    name: str
    email: str
    specialization: str = "general"


# Store conversation histories (in-memory for now)
conversation_sessions: dict[str, list] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    create_db_and_tables()
    # Seed some test doctors if empty
    with get_session() as session:
        from sqlmodel import select
        existing = session.exec(select(Doctor)).first()
        if not existing:
            doctors = [
                Doctor(name="Dr. Sarah Johnson", email="sarah@clinic.com", specialization=Specialization.GENERAL),
                Doctor(name="Dr. Michael Chen", email="michael@clinic.com", specialization=Specialization.CARDIOLOGY),
                Doctor(name="Dr. Emily Williams", email="emily@clinic.com", specialization=Specialization.DERMATOLOGY),
                Doctor(name="Dr. James Brown", email="james@clinic.com", specialization=Specialization.NEUROLOGY),
            ]
            for doc in doctors:
                session.add(doc)
            session.commit()
            print("✓ Seeded 4 doctors into database")
    yield


app = FastAPI(
    title="Medical Appointment System",
    description="MCP-based medical appointment booking with AI agent",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint to verify server is running."""
    return {"status": "healthy", "service": "medical-appointment-api"}


@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint with API info."""
    return {
        "message": "Medical Appointment System API",
        "docs": "/docs",
        "health": "/health"
    }


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint for the AI medical assistant.
    
    Processes user messages through the LLM agent and returns responses.
    """
    import uuid
    from agent import chat
    
    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    
    # Get existing conversation history or start new
    history = conversation_sessions.get(session_id, None)
    
    try:
        response, updated_history = chat(request.message, history)
        conversation_sessions[session_id] = updated_history
        
        return ChatResponse(
            response=response,
            session_id=session_id
        )
    except Exception as e:
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
            raise HTTPException(status_code=400, detail=f"Invalid specialization: {doctor.specialization}")
        
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
