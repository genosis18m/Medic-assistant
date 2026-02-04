"""
Database models for the Medical Appointment System.
"""
from sqlmodel import SQLModel, Field
from datetime import datetime, date, time
from typing import Optional
from enum import Enum


class AppointmentStatus(str, Enum):
    """Status of an appointment."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Specialization(str, Enum):
    """Medical specializations."""
    GENERAL = "general"
    CARDIOLOGY = "cardiology"
    DERMATOLOGY = "dermatology"
    NEUROLOGY = "neurology"
    ORTHOPEDICS = "orthopedics"
    PEDIATRICS = "pediatrics"


class Doctor(SQLModel, table=True):
    """Doctor model representing medical professionals."""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(unique=True)
    specialization: Specialization = Field(default=Specialization.GENERAL)
    available_from: time = Field(default=time(9, 0))  # 9 AM
    available_to: time = Field(default=time(17, 0))   # 5 PM
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Appointment(SQLModel, table=True):
    """Appointment model for booking slots."""
    id: Optional[int] = Field(default=None, primary_key=True)
    doctor_id: int = Field(foreign_key="doctor.id", index=True)
    patient_name: str
    patient_email: str
    appointment_date: date
    appointment_time: time
    reason: str = Field(default="General checkup")
    status: AppointmentStatus = Field(default=AppointmentStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
