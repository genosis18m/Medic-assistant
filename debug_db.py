import os
from sqlmodel import Session, select, create_engine
from backend.models import Appointment

DATABASE_URL = "postgresql://neondb_owner:npg_7B6ImGtOfEWT@ep-lingering-band-ai6apj2l-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"
engine = create_engine(DATABASE_URL)

def check_db():
    try:
        with Session(engine) as session:
            print("\n--- Last 10 Appointments ---")
            statement = select(Appointment).order_by(Appointment.id.desc()).limit(10)
            results = session.exec(statement).all()
            
            for apt in results:
                print(f"ID: {apt.id} | Patient: {apt.patient_name} ({apt.patient_email}) | Date: {apt.appointment_date} {apt.appointment_time} | Status: {apt.status}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_db()
