"""
Email Service for sending appointment confirmations and notifications.

Supports Gmail SMTP and can be extended for other providers.
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

# Email configuration
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "Medical Assistant")

# Check if email is configured
EMAIL_ENABLED = bool(SMTP_USER and SMTP_PASSWORD)


def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    text_body: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send an email using SMTP.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_body: HTML content of the email
        text_body: Plain text fallback
        
    Returns:
        Dict with success status and message
    """
    if not EMAIL_ENABLED:
        print("⚠️ Email not configured. Skipping email send.")
        return {
            "success": False,
            "error": "Email service not configured",
            "skipped": True
        }
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{EMAIL_FROM_NAME} <{SMTP_USER}>"
        msg['To'] = to_email
        
        # Attach plain text and HTML versions
        if text_body:
            msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send email
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        
        print(f"✅ Email sent to {to_email}")
        return {
            "success": True,
            "message": f"Email sent to {to_email}"
        }
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def send_booking_confirmation(
    patient_name: str,
    patient_email: str,
    doctor_name: str,
    doctor_specialization: str,
    appointment_date: str,
    appointment_time: str,
    appointment_id: int,
    reason: str = "Medical Consultation"
) -> Dict[str, Any]:
    """
    Send a booking confirmation email to the patient.
    """
    subject = f"✅ Appointment Confirmed - {doctor_name} on {appointment_date}"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #0d9488 0%, #0284c7 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center; }}
            .content {{ background: #f8fafc; padding: 30px; border: 1px solid #e2e8f0; }}
            .appointment-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin: 20px 0; }}
            .detail-row {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #e2e8f0; }}
            .detail-label {{ color: #64748b; font-weight: 500; }}
            .detail-value {{ color: #1e293b; font-weight: 600; }}
            .footer {{ background: #1e293b; color: #94a3b8; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; font-size: 12px; }}
            .btn {{ display: inline-block; background: #0d9488; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏥 Appointment Confirmed!</h1>
                <p>Your medical appointment has been scheduled</p>
            </div>
            <div class="content">
                <p>Dear <strong>{patient_name}</strong>,</p>
                <p>Your appointment has been successfully booked. Here are the details:</p>
                
                <div class="appointment-card">
                    <div class="detail-row">
                        <span class="detail-label">📋 Appointment ID</span>
                        <span class="detail-value">#{appointment_id}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">👨‍⚕️ Doctor</span>
                        <span class="detail-value">{doctor_name}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">🏷️ Specialization</span>
                        <span class="detail-value">{doctor_specialization.title()}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">📅 Date</span>
                        <span class="detail-value">{appointment_date}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">⏰ Time</span>
                        <span class="detail-value">{appointment_time}</span>
                    </div>
                    <div class="detail-row" style="border-bottom: none;">
                        <span class="detail-label">📝 Reason</span>
                        <span class="detail-value">{reason}</span>
                    </div>
                </div>
                
                <p><strong>📍 Important:</strong> Please arrive 10 minutes before your scheduled time.</p>
                <p>If you need to cancel or reschedule, please contact us at least 24 hours in advance.</p>
            </div>
            <div class="footer">
                <p>Medical Assistant - AI-Powered Healthcare</p>
                <p>This is an automated message. Please do not reply directly to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_body = f"""
    Appointment Confirmed!
    
    Dear {patient_name},
    
    Your appointment has been successfully booked.
    
    Details:
    - Appointment ID: #{appointment_id}
    - Doctor: {doctor_name}
    - Specialization: {doctor_specialization}
    - Date: {appointment_date}
    - Time: {appointment_time}
    - Reason: {reason}
    
    Please arrive 10 minutes before your scheduled time.
    
    If you need to cancel or reschedule, please contact us at least 24 hours in advance.
    
    - Medical Assistant
    """
    
    return send_email(patient_email, subject, html_body, text_body)


def send_cancellation_notice(
    patient_name: str,
    patient_email: str,
    doctor_name: str,
    appointment_date: str,
    appointment_time: str,
    appointment_id: int
) -> Dict[str, Any]:
    """
    Send a cancellation confirmation email to the patient.
    """
    subject = f"❌ Appointment Cancelled - #{appointment_id}"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #dc2626; color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center; }}
            .content {{ background: #f8fafc; padding: 30px; border: 1px solid #e2e8f0; }}
            .footer {{ background: #1e293b; color: #94a3b8; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Appointment Cancelled</h1>
            </div>
            <div class="content">
                <p>Dear <strong>{patient_name}</strong>,</p>
                <p>Your appointment has been cancelled as requested.</p>
                
                <p><strong>Cancelled Appointment:</strong></p>
                <ul>
                    <li>Appointment ID: #{appointment_id}</li>
                    <li>Doctor: {doctor_name}</li>
                    <li>Date: {appointment_date}</li>
                    <li>Time: {appointment_time}</li>
                </ul>
                
                <p>If you would like to reschedule, please book a new appointment through our system.</p>
            </div>
            <div class="footer">
                <p>Medical Assistant - AI-Powered Healthcare</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(patient_email, subject, html_body)
