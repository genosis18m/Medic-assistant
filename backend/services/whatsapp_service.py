"""
WhatsApp Notification Service using Twilio

Sends messages and reports to doctors via WhatsApp.
"""
import os
from typing import Optional, Dict, Any
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")


def get_twilio_client() -> Optional[Client]:
    """Get Twilio client if credentials are configured."""
    if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
        return Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    return None


def send_whatsapp_message(to_phone: str, message: str) -> Dict[str, Any]:
    """
    Send a WhatsApp message to a phone number.
    
    Args:
        to_phone: Phone number in E.164 format (e.g., +1234567890)
        message: Message content
        
    Returns:
        dict with status and message SID or error
    """
    client = get_twilio_client()
    
    if not client:
        return {
            "success": False,
            "error": "Twilio credentials not configured. Add TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN to .env"
        }
    
    try:
        # Ensure phone number has whatsapp: prefix
        if not to_phone.startswith("whatsapp:"):
            to_phone = f"whatsapp:{to_phone}"
        
        # Send message
        twilio_message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=message,
            to=to_phone
        )
        
        return {
            "success": True,
            "message_sid": twilio_message.sid,
            "status": twilio_message.status,
            "to": to_phone
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to send WhatsApp message: {str(e)}"
        }


def send_doctor_report_whatsapp(
    doctor_phone: str,
    doctor_name: str,
    report_summary: str
) -> Dict[str, Any]:
    """
    Send a formatted doctor report via WhatsApp.
    
    Args:
        doctor_phone: Doctor's phone number
        doctor_name: Doctor's name
        report_summary: Report content
        
    Returns:
        dict with status
    """
    # Format message
    message = f"""
🏥 *Medical Assistant Report*

Hello Dr. {doctor_name},

{report_summary}

---
Sent via Medical Assistant AI
    """.strip()
    
    return send_whatsapp_message(doctor_phone, message)


def send_appointment_notification_whatsapp(
    doctor_phone: str,
    doctor_name: str,
    patient_name: str,
    appointment_date: str,
    appointment_time: str,
    reason: str
) -> Dict[str, Any]:
    """
    Send new appointment notification to doctor via WhatsApp.
    
    Args:
        doctor_phone: Doctor's phone number
        doctor_name: Doctor's name  
        patient_name: Patient name
        appointment_date: Appointment date
        appointment_time: Appointment time
        reason: Appointment reason
        
    Returns:
        dict with status
    """
    message = f"""
📅 *New Appointment Booked*

Hello Dr. {doctor_name},

*Patient:* {patient_name}
*Date:* {appointment_date}
*Time:* {appointment_time}
*Reason:* {reason}

Please check your calendar for details.

---
Medical Assistant AI
    """.strip()
    
    return send_whatsapp_message(doctor_phone, message)


# Test function
if __name__ == "__main__":
    result = send_whatsapp_message(
        "+1234567890",  # Replace with your WhatsApp number for testing
        "Hello from Medical Assistant! This is a test message."
    )
    print(result)
