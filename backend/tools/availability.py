"""
MCP Tool: Check Doctor Availability

This tool queries the database to find available time slots for doctors.
"""
from datetime import date, time, datetime, timedelta
from sqlmodel import select
from typing import Optional

from database import get_session
from models import Doctor, Appointment, Specialization


def get_booked_slots(doctor_id: int, check_date: date) -> list[time]:
    """Get all booked time slots for a doctor on a specific date."""
    with get_session() as session:
        statement = select(Appointment).where(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == check_date
        )
        appointments = session.exec(statement).all()
        return [apt.appointment_time for apt in appointments]


def generate_time_slots(start: time, end: time, duration_minutes: int = 30) -> list[time]:
    """Generate available time slots between start and end times."""
    slots = []
    current = datetime.combine(date.today(), start)
    end_dt = datetime.combine(date.today(), end)
    
    while current < end_dt:
        slots.append(current.time())
        current += timedelta(minutes=duration_minutes)
    
    return slots


def check_availability(
    check_date: str,
    specialization: Optional[str] = None,
    doctor_id: Optional[int] = None
) -> dict:
    """
    Check available appointment slots for a given date.
    
    Args:
        check_date: Date to check in YYYY-MM-DD format
        specialization: Optional filter by doctor specialization
        doctor_id: Optional specific doctor ID to check
        
    Returns:
        Dictionary with doctor availability information
    """
    try:
        try:
            parsed_date = datetime.strptime(check_date, "%Y-%m-%d").date()
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD"}
        
        # Don't allow past dates
        if parsed_date < date.today():
            return {"error": "Cannot check availability for past dates"}
        
        with get_session() as session:
            # Build query for doctors
            statement = select(Doctor)
            
            if doctor_id:
                statement = statement.where(Doctor.id == doctor_id)
            elif specialization:
                try:
                    spec = Specialization(specialization.lower())
                    statement = statement.where(Doctor.specialization == spec)
                except ValueError:
                    return {"error": f"Invalid specialization: {specialization}"}
            
            doctors = session.exec(statement).all()
            
            if not doctors:
                return {"message": "No doctors found matching criteria", "availability": []}
            
            availability = []
            
            for doctor in doctors:
                # Generate all possible slots
                all_slots = generate_time_slots(
                    doctor.available_from,
                    doctor.available_to
                )
                
                # Get booked slots
                booked = get_booked_slots(doctor.id, parsed_date)
                
                # Calculate available slots
                available_slots = [
                    slot.strftime("%H:%M") for slot in all_slots 
                    if slot not in booked
                ]
                
                availability.append({
                    "doctor_id": doctor.id,
                    "doctor_name": doctor.name,
                    "specialization": doctor.specialization.value,
                    "date": check_date,
                    "available_slots": available_slots,
                    "total_available": len(available_slots)
                })
            
            return {
                "date": check_date,
                "availability": availability,
                "total_doctors": len(availability)
            }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"Internal Error checking availability: {str(e)}"}
