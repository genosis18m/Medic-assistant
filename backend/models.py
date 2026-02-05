"""
Database models for the Medical Appointment System.
Enhanced with patient tracking, symptoms, and visit notes.
"""
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, date, time
from typing import Optional, List
from enum import Enum


class UserRole(str, Enum):
    """User roles in the system."""
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"


class AppointmentStatus(str, Enum):
    """Status of an appointment."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"


class Specialization(str, Enum):
    """Medical specializations."""
    GENERAL = "general"
    CARDIOLOGY = "cardiology"
    DERMATOLOGY = "dermatology"
    NEUROLOGY = "neurology"
    ORTHOPEDICS = "orthopedics"
    PEDIATRICS = "pediatrics"


class User(SQLModel, table=True):
    """User model for authentication (bonus feature)."""
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    role: UserRole = Field(default=UserRole.PATIENT)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Doctor(SQLModel, table=True):
    """Doctor model representing medical professionals."""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(unique=True)
    specialization: Specialization = Field(default=Specialization.GENERAL)
    available_from: time = Field(default=time(9, 0))  # 9 AM
    available_to: time = Field(default=time(17, 0))   # 5 PM
    calendar_id: Optional[str] = Field(default=None)  # Google Calendar ID
    slack_user_id: Optional[str] = Field(default=None)  # For direct Slack DMs
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Patient(SQLModel, table=True):
    """Patient model for tracking patient information."""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(unique=True, index=True)
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    medical_history: Optional[str] = None  # JSON string of conditions
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Appointment(SQLModel, table=True):
    """Appointment model for booking slots with enhanced tracking."""
    id: Optional[int] = Field(default=None, primary_key=True)
    doctor_id: int = Field(foreign_key="doctor.id", index=True)
    patient_id: Optional[int] = Field(default=None, foreign_key="patient.id", index=True)
    patient_name: str
    patient_email: str
    appointment_date: date = Field(index=True)
    appointment_time: time
    reason: str = Field(default="General checkup")
    symptoms: Optional[str] = None  # Comma-separated symptoms
    status: AppointmentStatus = Field(default=AppointmentStatus.PENDING)
    
    # Post-visit fields
    visit_notes: Optional[str] = None
    diagnosis: Optional[str] = None
    prescription: Optional[str] = None
    
    # External integrations
    google_event_id: Optional[str] = None  # Google Calendar event ID
    email_sent: bool = Field(default=False)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PromptHistory(SQLModel, table=True):
    """Track prompt history for analytics (bonus feature)."""
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(index=True)
    role: UserRole
    user_prompt: str
    assistant_response: str
    tools_used: Optional[str] = None  # JSON array of tool names
    created_at: datetime = Field(default_factory=datetime.utcnow)
