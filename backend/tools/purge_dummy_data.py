from sqlmodel import Session, select, delete
from database import sync_engine as engine
from models import Patient, Appointment, User

def purge_dummy_data():
    with Session(engine) as session:
        print("Starting purge of dummy data...")
        
        # 1. Find the Demo Patient
        demo_patient_email = "demo@patient.com"
        patient = session.exec(select(Patient).where(Patient.email == demo_patient_email)).first()
        
        if patient:
            print(f"Found Demo Patient: {patient.name} (ID: {patient.id})")
            
            # 2. Delete all appointments for this patient
            statement = delete(Appointment).where(Appointment.patient_id == patient.id)
            result = session.exec(statement)
            session.commit()
            print(f"Deleted {result.rowcount} appointments for Demo Patient.")
            
            # 3. Delete the Patient record
            session.delete(patient)
            session.commit()
            print("Deleted Demo Patient record.")
            
        else:
            print("Demo Patient not found. Checking for orphaned demo appointments...")

        # 4. Safety net: Delete any appointments with 'demo@patient.com' just in case
        statement_orphans = delete(Appointment).where(Appointment.patient_email == "demo@patient.com")
        result_orphans = session.exec(statement_orphans)
        session.commit()
        if result_orphans.rowcount > 0:
            print(f"Deleted {result_orphans.rowcount} orphaned demo appointments.")

        print("Purge complete!")

if __name__ == "__main__":
    purge_dummy_data()
