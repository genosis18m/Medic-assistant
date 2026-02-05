"""
MCP Tool: Book Appointment

This tool creates new appointments with Google Calendar and email integration.
"""
from datetime import date, time, datetime
from sqlmodel import select
from typing import Optional

from database import get_session
from models import Doctor, Appointment, AppointmentStatus
from tools.availability import check_availability

# Import services (they handle their own configuration checks)
from services.google_calendar import create_appointment_event
from services.email_service import send_booking_confirmation, send_cancellation_notice
from services.slack_service import send_new_appointment_notification


def book_appointment(
    doctor_id: int,
    patient_name: str,
    patient_email: str,
    appointment_date: str,
    appointment_time: str,
    reason: Optional[str] = "General checkup",
    symptoms: Optional[str] = None
) -> dict:
    """
    Book an appointment with a doctor.
    
    Automatically:
    - Creates a Google Calendar event (if configured)
    - Sends email confirmation to patient (if configured)
    - Notifies doctor via Slack (if configured)
    
    Args:
        doctor_id: ID of the doctor to book with
        patient_name: Name of the patient
        patient_email: Email of the patient
        appointment_date: Date in YYYY-MM-DD format
        appointment_time: Time in HH:MM format
        reason: Optional reason for appointment
        symptoms: Optional comma-separated symptoms
        
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
            symptoms=symptoms,
            status=AppointmentStatus.CONFIRMED
        )
        
        session.add(appointment)
        session.commit()
        session.refresh(appointment)
        
        # Create Visit record for patient history tracking
        from models import Visit
        visit = Visit(
            appointment_id=appointment.id,
            patient_name=patient_name,
            patient_email=patient_email,
            doctor_id=doctor_id,
            visit_date=parsed_date,
            visit_time=parsed_time,
            reason=reason or "General checkup",
            symptoms=symptoms
        )
        session.add(visit)
        session.commit()
        
        # Prepare response
        result = {
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
            },
            "integrations": {}
        }
        
        # Try to create Google Calendar event
        calendar_result = create_appointment_event(
            doctor_name=doctor.name,
            patient_name=patient_name,
            patient_email=patient_email,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            reason=reason or "Medical Appointment"
        )
        
        if calendar_result.get("success"):
            appointment.google_event_id = calendar_result.get("event_id")
            session.add(appointment)
            session.commit()
            result["integrations"]["calendar"] = "Event created"
        else:
            result["integrations"]["calendar"] = calendar_result.get("error", "Not configured")
        
        # Try to send email confirmation
        email_result = send_booking_confirmation(
            patient_name=patient_name,
            patient_email=patient_email,
            doctor_name=doctor.name,
            doctor_specialization=doctor.specialization.value,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            appointment_id=appointment.id,
            reason=reason or "Medical Consultation"
        )
        
        if email_result.get("success"):
            appointment.email_sent = True
            session.add(appointment)
            session.commit()
            result["integrations"]["email"] = "Confirmation sent"
        else:
            result["integrations"]["email"] = email_result.get("error", "Not configured")
        
        # Try to notify doctor via Slack
        slack_result = send_new_appointment_notification(
            doctor_name=doctor.name,
            patient_name=patient_name,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            reason=reason or "Medical Consultation"
        )
        
        if slack_result.get("success"):
            result["integrations"]["slack"] = "Doctor notified"
        else:
            result["integrations"]["slack"] = slack_result.get("error", "Not configured")
        
        return result


def cancel_appointment(appointment_id: int) -> dict:
    """
    Cancel an existing appointment.
    
    Automatically:
    - Deletes Google Calendar event (if exists)
    - Sends cancellation email (if configured)
    
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
        
        # Get doctor info for notifications
        doctor = session.get(Doctor, appointment.doctor_id)
        doctor_name = doctor.name if doctor else "Unknown Doctor"
        
        # Cancel the appointment
        appointment.status = AppointmentStatus.CANCELLED
        session.add(appointment)
        session.commit()
        
        result = {
            "success": True,
            "message": f"Appointment {appointment_id} has been cancelled",
            "integrations": {}
        }
        
        # Try to delete Google Calendar event
        if appointment.google_event_id:
            from services.google_calendar import calendar_service
            calendar_result = calendar_service.delete_event(appointment.google_event_id)
            if calendar_result.get("success"):
                result["integrations"]["calendar"] = "Event deleted"
            else:
                result["integrations"]["calendar"] = calendar_result.get("error", "Failed")
        
        # Try to send cancellation email
        email_result = send_cancellation_notice(
            patient_name=appointment.patient_name,
            patient_email=appointment.patient_email,
            doctor_name=doctor_name,
            appointment_date=appointment.appointment_date.isoformat(),
            appointment_time=appointment.appointment_time.strftime("%H:%M"),
            appointment_id=appointment_id
        )
        
        if email_result.get("success"):
            result["integrations"]["email"] = "Cancellation notice sent"
        else:
            result["integrations"]["email"] = email_result.get("error", "Not configured")
        
        return result


def list_appointments(
    patient_email: Optional[str] = None,
    doctor_id: Optional[int] = None,
    date_str: Optional[str] = None,
    status: Optional[str] = None
) -> dict:
    """
    List appointments with flexible filtering.
    
    Args:
        patient_email: Optional email to filter appointments
        doctor_id: Optional doctor ID to filter
        date_str: Optional date to filter (YYYY-MM-DD)
        status: Optional status filter (pending, confirmed, completed, cancelled)
        
    Returns:
        Dictionary with list of appointments
    """
    with get_session() as session:
        statement = select(Appointment)
        
        if patient_email:
            statement = statement.where(Appointment.patient_email == patient_email)
        
        if doctor_id:
            statement = statement.where(Appointment.doctor_id == doctor_id)
        
        if date_str:
            try:
                parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                statement = statement.where(Appointment.appointment_date == parsed_date)
            except ValueError:
                return {"success": False, "error": "Invalid date format. Use YYYY-MM-DD"}
        
        if status:
            try:
                status_enum = AppointmentStatus(status.lower())
                statement = statement.where(Appointment.status == status_enum)
            except ValueError:
                pass  # Ignore invalid status
        
        # Order by date and time
        statement = statement.order_by(
            Appointment.appointment_date,
            Appointment.appointment_time
        )
        
        appointments = session.exec(statement).all()
        
        result = []
        for apt in appointments:
            doctor = session.get(Doctor, apt.doctor_id)
            result.append({
                "id": apt.id,
                "doctor_id": apt.doctor_id,
                "doctor_name": doctor.name if doctor else "Unknown",
                "doctor_specialization": doctor.specialization.value if doctor else "unknown",
                "patient_name": apt.patient_name,
                "patient_email": apt.patient_email,
                "appointment_date": apt.appointment_date.isoformat(),
                "appointment_time": apt.appointment_time.strftime("%H:%M"),
                "reason": apt.reason,
                "symptoms": apt.symptoms,
                "status": apt.status.value,
                "email_sent": apt.email_sent if hasattr(apt, 'email_sent') else False
            })
        
        return {
            "success": True,
            "total": len(result),
            "appointments": result
        }
