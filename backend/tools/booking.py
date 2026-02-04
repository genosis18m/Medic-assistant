"""
MCP Tool: Book Appointment

This tool creates new appointments in the database.
"""
from datetime import date, time, datetime
from sqlmodel import select
from typing import Optional

from database import get_session
from models import Doctor, Appointment, AppointmentStatus
from tools.availability import check_availability


def book_appointment(
    doctor_id: int,
    patient_name: str,
    patient_email: str,
    appointment_date: str,
    appointment_time: str,
    reason: Optional[str] = "General checkup"
) -> dict:
    """
    Book an appointment with a doctor.
    
    Args:
        doctor_id: ID of the doctor to book with
        patient_name: Name of the patient
        patient_email: Email of the patient
        appointment_date: Date in YYYY-MM-DD format
        appointment_time: Time in HH:MM format
        reason: Optional reason for appointment
        
    Returns:
        Dictionary with booking confirmation or error
    """
    # Validate date format
    try:
        parsed_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()
    except ValueError:
        return {"success": False, "error": "Invalid date format. Use YYYY-MM-DD"}
    
    # Validate time format
    try:
        parsed_time = datetime.strptime(appointment_time, "%H:%M").time()
    except ValueError:
        return {"success": False, "error": "Invalid time format. Use HH:MM"}
    
    # Don't allow past dates
    if parsed_date < date.today():
        return {"success": False, "error": "Cannot book appointments in the past"}
    
    with get_session() as session:
        # Check if doctor exists
        doctor = session.get(Doctor, doctor_id)
        if not doctor:
            return {"success": False, "error": f"Doctor with ID {doctor_id} not found"}
        
        # Check if time is within doctor's hours
        if parsed_time < doctor.available_from or parsed_time >= doctor.available_to:
            return {
                "success": False,
                "error": f"Doctor is only available between {doctor.available_from.strftime('%H:%M')} and {doctor.available_to.strftime('%H:%M')}"
            }
        
        # Check if slot is available
        existing = session.exec(
            select(Appointment).where(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_date == parsed_date,
                Appointment.appointment_time == parsed_time,
                Appointment.status != AppointmentStatus.CANCELLED
            )
        ).first()
        
        if existing:
            return {
                "success": False,
                "error": f"Time slot {appointment_time} on {appointment_date} is already booked"
            }
        
        # Create appointment
        appointment = Appointment(
            doctor_id=doctor_id,
            patient_name=patient_name,
            patient_email=patient_email,
            appointment_date=parsed_date,
            appointment_time=parsed_time,
            reason=reason or "General checkup",
            status=AppointmentStatus.CONFIRMED
        )
        
        session.add(appointment)
        session.commit()
        session.refresh(appointment)
        
        return {
            "success": True,
            "message": "Appointment booked successfully",
            "appointment": {
                "id": appointment.id,
                "doctor": doctor.name,
                "doctor_specialization": doctor.specialization.value,
                "patient": patient_name,
                "date": appointment_date,
                "time": appointment_time,
                "reason": appointment.reason,
                "status": appointment.status.value
            }
        }


def cancel_appointment(appointment_id: int) -> dict:
    """
    Cancel an existing appointment.
    
    Args:
        appointment_id: ID of the appointment to cancel
        
    Returns:
        Dictionary with cancellation confirmation or error
    """
    with get_session() as session:
        appointment = session.get(Appointment, appointment_id)
        
        if not appointment:
            return {"success": False, "error": f"Appointment {appointment_id} not found"}
        
        if appointment.status == AppointmentStatus.CANCELLED:
            return {"success": False, "error": "Appointment is already cancelled"}
        
        appointment.status = AppointmentStatus.CANCELLED
        session.add(appointment)
        session.commit()
        
        return {
            "success": True,
            "message": f"Appointment {appointment_id} has been cancelled"
        }


def list_appointments(patient_email: Optional[str] = None) -> dict:
    """
    List appointments, optionally filtered by patient email.
    
    Args:
        patient_email: Optional email to filter appointments
        
    Returns:
        Dictionary with list of appointments
    """
    with get_session() as session:
        statement = select(Appointment)
        
        if patient_email:
            statement = statement.where(Appointment.patient_email == patient_email)
        
        appointments = session.exec(statement).all()
        
        result = []
        for apt in appointments:
            doctor = session.get(Doctor, apt.doctor_id)
            result.append({
                "id": apt.id,
                "doctor": doctor.name if doctor else "Unknown",
                "patient": apt.patient_name,
                "date": apt.appointment_date.isoformat(),
                "time": apt.appointment_time.strftime("%H:%M"),
                "reason": apt.reason,
                "status": apt.status.value
            })
        
        return {
            "total": len(result),
            "appointments": result
        }
