"""
MCP Tools: Doctor Reports and Statistics

Tools for querying appointment data and generating reports for doctors.
"""
from datetime import date, datetime, timedelta
from sqlmodel import select, func
from typing import Optional, List, Dict, Any

from database import get_session
from models import Doctor, Appointment, AppointmentStatus
from services.slack_service import send_doctor_summary_report


def get_appointment_stats(
    doctor_id: Optional[int] = None,
    date_str: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get appointment statistics for a doctor within a date range.
    
    Args:
        doctor_id: Optional specific doctor ID
        date_str: Single date in YYYY-MM-DD format (for "today", "yesterday" queries)
        start_date: Start of date range in YYYY-MM-DD format
        end_date: End of date range in YYYY-MM-DD format
        
    Returns:
        Dictionary with appointment statistics
    """
    try:
        # Parse dates
        if date_str:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            query_start = target_date
            query_end = target_date
        elif start_date and end_date:
            query_start = datetime.strptime(start_date, "%Y-%m-%d").date()
            query_end = datetime.strptime(end_date, "%Y-%m-%d").date()
        else:
            # Default to today
            query_start = date.today()
            query_end = date.today()
        
        with get_session() as session:
            # Build base query
            statement = select(Appointment).where(
                Appointment.appointment_date >= query_start,
                Appointment.appointment_date <= query_end
            )
            
            if doctor_id:
                statement = statement.where(Appointment.doctor_id == doctor_id)
            
            appointments = session.exec(statement).all()
            
            # Calculate stats
            stats = {
                "total": len(appointments),
                "confirmed": sum(1 for a in appointments if a.status == AppointmentStatus.CONFIRMED),
                "pending": sum(1 for a in appointments if a.status == AppointmentStatus.PENDING),
                "completed": sum(1 for a in appointments if a.status == AppointmentStatus.COMPLETED),
                "cancelled": sum(1 for a in appointments if a.status == AppointmentStatus.CANCELLED),
                "no_show": sum(1 for a in appointments if a.status == AppointmentStatus.NO_SHOW)
            }
            
            # Get doctor names for context
            doctor_names = {}
            if not doctor_id:
                for apt in appointments:
                    if apt.doctor_id not in doctor_names:
                        doctor = session.get(Doctor, apt.doctor_id)
                        doctor_names[apt.doctor_id] = doctor.name if doctor else "Unknown"
            
            # Format date range
            if query_start == query_end:
                date_range_str = query_start.strftime("%B %d, %Y")
            else:
                date_range_str = f"{query_start.strftime('%B %d')} - {query_end.strftime('%B %d, %Y')}"
            
            return {
                "success": True,
                "date_range": date_range_str,
                "stats": stats,
                "message": f"Found {stats['total']} appointments for {date_range_str}"
            }
            
    except ValueError as e:
        return {"success": False, "error": f"Invalid date format: {e}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_patient_stats(
    symptoms: Optional[str] = None,
    diagnosis: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    doctor_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get patient statistics, optionally filtered by symptoms or diagnosis.
    
    Args:
        symptoms: Symptoms to search for (e.g., "fever", "headache")
        diagnosis: Diagnosis to search for
        start_date: Start of date range in YYYY-MM-DD format
        end_date: End of date range in YYYY-MM-DD format
        doctor_id: Optional specific doctor ID
        
    Returns:
        Dictionary with patient statistics and list
    """
    try:
        # Default date range: last 7 days
        if start_date:
            query_start = datetime.strptime(start_date, "%Y-%m-%d").date()
        else:
            query_start = date.today() - timedelta(days=7)
        
        if end_date:
            query_end = datetime.strptime(end_date, "%Y-%m-%d").date()
        else:
            query_end = date.today()
        
        with get_session() as session:
            # Build query
            statement = select(Appointment).where(
                Appointment.appointment_date >= query_start,
                Appointment.appointment_date <= query_end
            )
            
            if doctor_id:
                statement = statement.where(Appointment.doctor_id == doctor_id)
            
            appointments = session.exec(statement).all()
            
            # Filter by symptoms or diagnosis
            filtered_appointments = []
            for apt in appointments:
                include = True
                
                if symptoms:
                    symptoms_lower = symptoms.lower()
                    apt_symptoms = (apt.symptoms or "").lower()
                    apt_reason = (apt.reason or "").lower()
                    include = symptoms_lower in apt_symptoms or symptoms_lower in apt_reason
                
                if diagnosis and include:
                    diagnosis_lower = diagnosis.lower()
                    apt_diagnosis = (apt.diagnosis or "").lower()
                    include = diagnosis_lower in apt_diagnosis
                
                if include:
                    doctor = session.get(Doctor, apt.doctor_id)
                    filtered_appointments.append({
                        "id": apt.id,
                        "patient_name": apt.patient_name,
                        "patient_email": apt.patient_email,
                        "date": apt.appointment_date.isoformat(),
                        "time": apt.appointment_time.strftime("%H:%M"),
                        "symptoms": apt.symptoms,
                        "reason": apt.reason,
                        "diagnosis": apt.diagnosis,
                        "doctor": doctor.name if doctor else "Unknown",
                        "status": apt.status.value
                    })
            
            filter_desc = []
            if symptoms:
                filter_desc.append(f"symptoms containing '{symptoms}'")
            if diagnosis:
                filter_desc.append(f"diagnosis containing '{diagnosis}'")
            
            return {
                "success": True,
                "total_patients": len(filtered_appointments),
                "date_range": f"{query_start.isoformat()} to {query_end.isoformat()}",
                "filters_applied": filter_desc if filter_desc else ["none"],
                "patients": filtered_appointments,
                "message": f"Found {len(filtered_appointments)} patients"
            }
            
    except ValueError as e:
        return {"success": False, "error": f"Invalid date format: {e}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def generate_summary_report(
    doctor_id: int,
    report_type: str = "daily",
    date_str: Optional[str] = None,
    send_notification: bool = False
) -> Dict[str, Any]:
    """
    Generate a human-readable summary report for a doctor.
    
    Args:
        doctor_id: ID of the doctor
        report_type: Type of report ("daily", "weekly", "custom")
        date_str: Specific date for daily report (YYYY-MM-DD), defaults to today
        send_notification: Whether to send the report via Slack
        
    Returns:
        Dictionary with formatted report
    """
    try:
        # Determine date range based on report type
        if date_str:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        else:
            target_date = date.today()
        
        if report_type == "daily":
            query_start = target_date
            query_end = target_date
        elif report_type == "weekly":
            query_start = target_date - timedelta(days=target_date.weekday())
            query_end = query_start + timedelta(days=6)
        else:
            query_start = target_date
            query_end = target_date
        
        with get_session() as session:
            # Get doctor info
            doctor = session.get(Doctor, doctor_id)
            if not doctor:
                return {"success": False, "error": f"Doctor with ID {doctor_id} not found"}
            
            # Get appointments
            statement = select(Appointment).where(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_date >= query_start,
                Appointment.appointment_date <= query_end
            ).order_by(Appointment.appointment_date, Appointment.appointment_time)
            
            appointments = session.exec(statement).all()
            
            # Calculate stats
            stats = {
                "total": len(appointments),
                "confirmed": sum(1 for a in appointments if a.status == AppointmentStatus.CONFIRMED),
                "pending": sum(1 for a in appointments if a.status == AppointmentStatus.PENDING),
                "completed": sum(1 for a in appointments if a.status == AppointmentStatus.COMPLETED),
                "cancelled": sum(1 for a in appointments if a.status == AppointmentStatus.CANCELLED)
            }
            
            # Format appointments for report
            apt_list = [
                {
                    "id": apt.id,
                    "patient": apt.patient_name,
                    "time": apt.appointment_time.strftime("%H:%M"),
                    "date": apt.appointment_date.isoformat(),
                    "reason": apt.reason,
                    "status": apt.status.value
                }
                for apt in appointments
            ]
            
            # Format date string
            if query_start == query_end:
                date_range_str = query_start.strftime("%B %d, %Y")
            else:
                date_range_str = f"{query_start.strftime('%B %d')} - {query_end.strftime('%B %d, %Y')}"
            
            # Generate human-readable summary
            summary_lines = [
                f"📊 {report_type.title()} Report for {doctor.name}",
                f"📅 {date_range_str}",
                "",
                f"📋 Total Appointments: {stats['total']}",
                f"✅ Completed: {stats['completed']}",
                f"⏳ Pending/Confirmed: {stats['pending'] + stats['confirmed']}",
                f"❌ Cancelled: {stats['cancelled']}",
            ]
            
            if apt_list:
                summary_lines.append("")
                summary_lines.append("📝 Appointment Details:")
                for apt in apt_list[:10]:  # Limit to 10
                    status_symbol = {
                        "confirmed": "🟢",
                        "pending": "🟡",
                        "completed": "✅",
                        "cancelled": "🔴"
                    }.get(apt["status"], "⚪")
                    summary_lines.append(
                        f"  {status_symbol} {apt['time']} - {apt['patient']} ({apt['reason']})"
                    )
            
            report = {
                "success": True,
                "doctor": doctor.name,
                "date_range": date_range_str,
                "report_type": report_type,
                "stats": stats,
                "appointments": apt_list,
                "summary": "\n".join(summary_lines)
            }
            
            # Send notification if requested
            if send_notification:
                notification_result = send_doctor_summary_report(
                    doctor_name=doctor.name,
                    date_str=date_range_str,
                    stats=stats,
                    appointments=apt_list
                )
                report["notification_sent"] = notification_result.get("success", False)
                if not notification_result.get("success"):
                    report["notification_error"] = notification_result.get("error")
            
            return report
            
    except ValueError as e:
        return {"success": False, "error": f"Invalid date format: {e}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def send_slack_notification(
    doctor_id: int,
    message: Optional[str] = None,
    include_today_summary: bool = True
) -> Dict[str, Any]:
    """
    Send a notification to a doctor via Slack.
    
    Args:
        doctor_id: ID of the doctor
        message: Optional custom message to include
        include_today_summary: Whether to include today's appointment summary
        
    Returns:
        Dictionary with notification result
    """
    try:
        with get_session() as session:
            doctor = session.get(Doctor, doctor_id)
            if not doctor:
                return {"success": False, "error": f"Doctor with ID {doctor_id} not found"}
        
        if include_today_summary:
            # Generate and send today's summary
            result = generate_summary_report(
                doctor_id=doctor_id,
                report_type="daily",
                date_str=date.today().isoformat(),
                send_notification=True
            )
            
            if message and result.get("success"):
                # Also send custom message
                from services.slack_service import send_slack_message_sync
                send_slack_message_sync(f"📬 Message for {doctor.name}: {message}")
            
            return {
                "success": result.get("success", False),
                "message": "Summary report sent to Slack" if result.get("notification_sent") else "Failed to send notification",
                "report_summary": result.get("summary", "")
            }
        else:
            # Just send the custom message
            from services.slack_service import send_slack_message_sync
            result = send_slack_message_sync(f"📬 Message for {doctor.name}: {message or 'No message provided'}")
            return result
            
    except Exception as e:
        return {"success": False, "error": str(e)}
