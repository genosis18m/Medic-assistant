"""
Patient History Tools - MCP tools for viewing and managing patient visit history.
"""
from sqlmodel import Session, select
from datetime import datetime, date
from typing import Dict, Any, Optional, List
from models import Visit, Prescription, Appointment, Doctor
from database import get_session


def get_patient_history(patient_email: str, limit: int = 10) -> Dict[str, Any]:
    """Get complete visit history for a patient."""
    try:
        with get_session() as session:
            # Get all visits for this patient
            statement = select(Visit).where(
                Visit.patient_email == patient_email
            ).order_by(Visit.visit_date.desc()).limit(limit)
            
            visits = session.exec(statement).all()
            
            if not visits:
                return {
                    "success": False,
                    "message": f"No visit history found for {patient_email}"
                }
            
            # Format visit history
            history = []
            for visit in visits:
                # Get prescriptions for this visit
                presc_stmt = select(Prescription).where(Prescription.visit_id == visit.id)
                prescriptions = session.exec(presc_stmt).all()
                
                history.append({
                    "date": visit.visit_date.isoformat(),
                    "time": visit.visit_time.strftime("%H:%M"),
                    "reason": visit.reason,
                    "symptoms": visit.symptoms,
                    "diagnosis": visit.diagnosis,
                    "doctor_notes": visit.doctor_notes,
                    "prescriptions": [{
                        "medication": p.medication_name,
                        "dosage": p.dosage,
                        "frequency": p.frequency,
                        "duration": p.duration
                    } for p in prescriptions]
                })
            
            return {
                "success": True,
                "patient_email": patient_email,
                "total_visits": len(history),
                "visits": history
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}


def add_visit_notes(
    appointment_id: int,
    diagnosis: str,
    doctor_notes: Optional[str] = None
) -> Dict[str, Any]:
    """Add or update diagnosis and notes for a visit."""
    try:
        with get_session() as session:
            # Find the visit by appointment_id
            statement = select(Visit).where(Visit.appointment_id == appointment_id)
            visit = session.exec(statement).first()
            
            if not visit:
                return {
                    "success": False,
                    "error": f"No visit found for appointment {appointment_id}"
                }
            
            # Update visit
            visit.diagnosis = diagnosis
            visit.doctor_notes = doctor_notes
            visit.updated_at = datetime.utcnow()
            
            session.add(visit)
            session.commit()
            session.refresh(visit)
            
            return {
                "success": True,
                "message": f"Updated notes for {visit.patient_name}'s visit",
                "visit_id": visit.id,
                "diagnosis": diagnosis
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}


def add_prescription(
    visit_id: int,
    medication_name: str,
    dosage: str,
    frequency: str,
    duration: str,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """Add a prescription to a visit."""
    try:
        with get_session() as session:
            # Get visit to verify it exists and get patient name
            visit = session.get(Visit, visit_id)
            if not visit:
                return {
                    "success": False,
                    "error": f"Visit {visit_id} not found"
                }
            
            # Create prescription
            prescription = Prescription(
                visit_id=visit_id,
                patient_name=visit.patient_name,
                medication_name=medication_name,
                dosage=dosage,
                frequency=frequency,
                duration=duration,
                notes=notes
            )
            
            session.add(prescription)
            session.commit()
            session.refresh(prescription)
            
            return {
                "success": True,
                "message": f"Added prescription for {visit.patient_name}",
                "prescription_id": prescription.id,
                "medication": medication_name,
                "dosage": dosage
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}


def generate_patient_report(patient_email: str) -> Dict[str, Any]:
    """Generate comprehensive PDF report for a patient."""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.units import inch
    import os
    from io import BytesIO
    
    try:
        # Get patient history
        history_data = get_patient_history(patient_email, limit=50)
        
        if not history_data.get("success"):
            return history_data
        
        # Create PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph(f"<b>Medical Report - {patient_email}</b>", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Summary
        summary = Paragraph(f"Total Visits: {history_data['total_visits']}<br/>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal'])
        elements.append(summary)
        elements.append(Spacer(1, 0.3*inch))
        
        # Visit history
        for visit in history_data['visits']:
            # Visit header
            visit_header = Paragraph(f"<b>Visit: {visit['date']} at {visit['time']}</b>", styles['Heading2'])
            elements.append(visit_header)
            
            # Visit details
            details = f"""
            <b>Reason:</b> {visit['reason']}<br/>
            <b>Symptoms:</b> {visit['symptoms'] or 'N/A'}<br/>
            <b>Diagnosis:</b> {visit['diagnosis'] or 'Pending'}<br/>
            <b>Notes:</b> {visit['doctor_notes'] or 'N/A'}
            """
            elements.append(Paragraph(details, styles['Normal']))
            
            # Prescriptions
            if visit['prescriptions']:
                elements.append(Spacer(1, 0.1*inch))
                presc_data = [['Medication', 'Dosage', 'Frequency', 'Duration']]
                for p in visit['prescriptions']:
                    presc_data.append([
                        p['medication'],
                        p['dosage'],
                        p['frequency'],
                        p['duration']
                    ])
                
                presc_table = Table(presc_data, colWidths=[2*inch, 1*inch, 1.5*inch, 1*inch])
                presc_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(presc_table)
            
            elements.append(Spacer(1, 0.3*inch))
        
        # Build PDF
        doc.build(elements)
        
        # Save to file
        os.makedirs('reports', exist_ok=True)
        filename = f"reports/patient_{patient_email.replace('@', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        with open(filename, 'wb') as f:
            f.write(buffer.getvalue())
        
        return {
            "success": True,
            "message": f"Report generated successfully",
            "filename": filename,
            "total_visits": history_data['total_visits']
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
