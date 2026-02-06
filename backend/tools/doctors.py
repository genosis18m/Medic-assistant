from sqlmodel import select
from database import get_session
from models import Doctor

def list_doctors() -> dict:
    """List all available doctors."""
    with get_session() as session:
        doctors = session.exec(select(Doctor)).all()
        return {
            "doctors": [
                {
                    "id": d.id,
                    "name": d.name,
                    "email": d.email,
                    "specialization": d.specialization.value,
                    "available_from": d.available_from.strftime("%H:%M"),
                    "available_to": d.available_to.strftime("%H:%M"),
                    "phone_number": d.phone_number or "+919876543210" # Default for testing
                }
                for d in doctors
            ]
        }
