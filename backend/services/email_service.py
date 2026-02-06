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
    Send a minimal, professional booking confirmation email.
    """
    subject = f"Appointment Confirmed - {appointment_date}"
    
    # Clean, minimal design with subtle elegance
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #1a1a1a;
                background: #f9fafb;
                margin: 0;
                padding: 0;
            }}
            .email-wrapper {{
                max-width: 560px;
                margin: 40px auto;
                background: white;
            }}
            .header {{
                padding: 32px 40px 24px;
                border-bottom: 1px solid #e5e7eb;
            }}
            .logo {{
                font-size: 20px;
                font-weight: 600;
                color: #0d9488;
                margin: 0;
            }}
            .content {{
                padding: 32px 40px;
            }}
            .greeting {{
                font-size: 15px;
                color: #6b7280;
                margin: 0 0 24px;
            }}
            .appointment-box {{
                background: #f9fafb;
                border-left: 3px solid #0d9488;
                padding: 20px 24px;
                margin: 24px 0;
            }}
            .appointment-row {{
                display: flex;
                justify-content: space-between;
                padding: 8px 0;
            }}
            .label {{
                color: #6b7280;
                font-size: 14px;
            }}
            .value {{
                color: #1a1a1a;
                font-weight: 500;
                font-size: 14px;
                text-align: right;
            }}
            .note {{
                font-size: 13px;
                color: #6b7280;
                margin: 24px 0 0;
                padding: 16px;
                background: #fef9c3;
                border-radius: 4px;
            }}
            .footer {{
                padding: 24px 40px;
                border-top: 1px solid #e5e7eb;
                text-align: center;
            }}
            .footer-text {{
                font-size: 12px;
                color: #9ca3af;
                margin: 4px 0;
            }}
        </style>
    </head>
    <body>
        <div class="email-wrapper">
            <div class="header">
                <h1 class="logo">Medical Assistant</h1>
            </div>
            
            <div class="content">
                <p class="greeting">Hello {patient_name},</p>
                <p style="margin: 0 0 16px; font-size: 15px; color: #1a1a1a;">Your appointment has been confirmed.</p>
                
                <div class="appointment-box">
                    <div class="appointment-row">
                        <span class="label">Doctor</span>
                        <span class="value">{doctor_name}</span>
                    </div>
                    <div class="appointment-row">
                        <span class="label">Specialization</span>
                        <span class="value">{doctor_specialization.title()}</span>
                    </div>
                    <div class="appointment-row">
                        <span class="label">Date</span>
                        <span class="value">{appointment_date}</span>
                    </div>
                    <div class="appointment-row">
                        <span class="label">Time</span>
                        <span class="value">{appointment_time}</span>
                    </div>
                    <div class="appointment-row">
                        <span class="label">Reference</span>
                        <span class="value">#{appointment_id}</span>
                    </div>
                </div>
                
                <p class="note">
                    Please arrive 10 minutes early. To cancel or reschedule, contact us at least 24 hours in advance.
                </p>
            </div>
            
            <div class="footer">
                <p class="footer-text">Medical Assistant · AI-Powered Healthcare</p>
                <p class="footer-text">This is an automated message</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_body = f"""
    Appointment Confirmed
    
    Hello {patient_name},
    
    Your appointment has been confirmed.
    
    Doctor: {doctor_name}
    Specialization: {doctor_specialization}
    Date: {appointment_date}
    Time: {appointment_time}
    Reference: #{appointment_id}
    
    Please arrive 10 minutes early.
    To cancel or reschedule, contact us at least 24 hours in advance.
    
    Medical Assistant
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
    Send a minimal cancellation confirmation email.
    """
    subject = f"Appointment Cancelled - {appointment_date}"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #1a1a1a;
                background: #f9fafb;
                margin: 0;
                padding: 0;
            }}
            .email-wrapper {{
                max-width: 560px;
                margin: 40px auto;
                background: white;
            }}
            .header {{
                padding: 32px 40px 24px;
                border-bottom: 1px solid #e5e7eb;
            }}
            .logo {{
                font-size: 20px;
                font-weight: 600;
                color: #dc2626;
                margin: 0;
            }}
            .content {{
                padding: 32px 40px;
            }}
            .footer {{
                padding: 24px 40px;
                border-top: 1px solid #e5e7eb;
                text-align: center;
            }}
            .footer-text {{
                font-size: 12px;
                color: #9ca3af;
                margin: 4px 0;
            }}
        </style>
    </head>
    <body>
        <div class="email-wrapper">
            <div class="header">
                <h1 class="logo">Appointment Cancelled</h1>
            </div>
            
            <div class="content">
                <p>Hello {patient_name},</p>
                <p>Your appointment has been cancelled as requested.</p>
                
                <p><strong>Cancelled:</strong></p>
                <ul>
                    <li>Doctor: {doctor_name}</li>
                    <li>Date: {appointment_date}</li>
                    <li>Time: {appointment_time}</li>
                    <li>Reference: #{appointment_id}</li>
                </ul>
                
                <p>You can book a new appointment anytime through our system.</p>
            </div>
            
            <div class="footer">
                <p class="footer-text">Medical Assistant</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(patient_email, subject, html_body)
