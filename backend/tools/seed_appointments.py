from sqlmodel import Session, select
from datetime import date, datetime, timedelta, time
import random
from database import sync_engine
from models import Doctor, Appointment, AppointmentStatus

def seed_appointments():
    print("Seeding appointments for all doctors...")
    with Session(sync_engine) as session:
        # Get all doctors
        doctors = session.exec(select(Doctor)).all()
        if not doctors:
            print("No doctors found! Run main.py first.")
            return

        # Get or create dummy patient
        from models import Patient  # Correct model
        dummy_patient = session.exec(select(Patient).where(Patient.email == "demo@patient.com")).first()
        if not dummy_patient:
            dummy_patient = Patient(
                name="Demo Patient",
                email="demo@patient.com",
                phone="555-0123"
            )
            session.add(dummy_patient)
            session.commit()
            session.refresh(dummy_patient)
            print(f"Created demo patient with ID {dummy_patient.id}")

        today = date.today()
        dates = [today, today + timedelta(days=1), today + timedelta(days=2)]
        
        patient_names = ["John Doe", "Jane Smith", "Alice Brown", "Bob Wilson", "Carol White", "David Lee", "Eva Green"]
        reasons = ["Fever", "Headache", "Annual Checkup", "Back Pain", "Migraine", "Sore Throat", "Follow-up"]
        
        count = 0
        for doctor in doctors:
            print(f"Generating schedule for {doctor.name}...")
            for day in dates:
                # Randomly decide how many appointments (3-8 per day)
                num_appts = random.randint(3, 8)
                
                # Generate times between 9 AM and 5 PM
                available_hours = list(range(9, 17))
                selected_hours = random.sample(available_hours, num_appts)
                selected_hours.sort()
                
                for hour in selected_hours:
                    # Check if slot exists
                    appt_time = time(hour, 0)
                    existing = session.exec(select(Appointment).where(
                        Appointment.doctor_id == doctor.id,
                        Appointment.appointment_date == day,
                        Appointment.appointment_time == appt_time
                    )).first()
                    
                    if not existing:
                        appt = Appointment(
                            doctor_id=doctor.id,
                            patient_id=dummy_patient.id,  # Use real user ID
                            patient_name=random.choice(patient_names),
                            patient_email="demo@patient.com",
                            appointment_date=day,
                            appointment_time=appt_time,
                            reason=random.choice(reasons),
                            status=AppointmentStatus.CONFIRMED,
                            symptoms="Demo symptoms"
                        )
                        session.add(appt)
                        count += 1
        
        session.commit()
        print(f"✅ Successfully seeded {count} appointments across {len(doctors)} doctors!")

if __name__ == "__main__":
    seed_appointments()
