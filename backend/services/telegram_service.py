import os
import io
import httpx
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7719345675:AAG7JEINJbYVNXWgLNgyjZrZAw789FDo7mM")
TELEGRAM_BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

def generate_pdf_report(doctor_name: str, appointments: list, report_date: str) -> io.BytesIO:
    """
    Generate a PDF report with:
    - Count in the middle
    - List of people and time below
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Header
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height - 1 * inch, f"Appointment Report - {doctor_name}")
    
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 1.3 * inch, f"Date: {report_date}")
    
    # Big Count in Middle
    count = len(appointments)
    c.setFont("Helvetica-Bold", 36)
    c.setFillColor(colors.teal)
    c.drawCentredString(width / 2, height - 3 * inch, str(count))
    
    c.setFont("Helvetica", 14)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, height - 3.5 * inch, "Total Appointments")
    
    # Appointment List
    start_y = height - 5 * inch
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1 * inch, start_y, "Patient Visit List:")
    
    c.setFont("Helvetica", 12)
    y_position = start_y - 0.5 * inch
    
    for apt in appointments:
        if y_position < 1 * inch: # New page if full
            c.showPage()
            y_position = height - 1 * inch
            c.setFont("Helvetica", 12)
            
        time_str = apt.get("time", "N/A")
        patient_name = apt.get("patient_name", "Unknown")
        reason = apt.get("reason", "Checkup")
        
        line = f"• {time_str} - {patient_name} ({reason})"
        c.drawString(1.2 * inch, y_position, line)
        y_position -= 0.3 * inch
        
    c.save()
    buffer.seek(0)
    return buffer

# Map phone numbers to Telegram chat_id. To link a doctor: they send /start to the bot
# (e.g. @Doctor_AssistBot); the bot stores their chat_id keyed by phone; we look up here.
PHONE_TO_CHAT_ID = {
    "9876543210": "1705662369", # Example ID for Dr. Mohit
    "5551234567": "1705662369", # Dr. Michael Chen (using same ID for testing)
    "919876543210": "1705662369", # Dr. Michael Chen (Specific test number)
    "+919876543210": "1705662369", # Dr. Michael Chen (With prefix)
}


async def send_telegram_pdf(chat_id: str = None, phone_number: str = None, pdf_file: io.BytesIO = None, filename: str = "report.pdf"):
    """
    Send generated PDF to Telegram chat.
    Resolves phone_number to chat_id if necessary.
    """
    if not chat_id and phone_number:
        # Clean phone number
        phone = phone_number.replace("+", "").replace(" ", "").replace("-", "")
        chat_id = PHONE_TO_CHAT_ID.get(phone)
        
        if not chat_id:
            return {
                "success": False, 
                "error": f"No Telegram Chat ID found for phone {phone_number}. Please ask the doctor to start the bot @Doctor_AssistBot so we can link their account."
            }

    if not chat_id:
        return {"success": False, "error": "No Chat ID provided and Phone Number resolution failed."}

    url = f"{TELEGRAM_BASE_URL}/sendDocument"
    
    try:
        # Reset file pointer
        pdf_file.seek(0)
        
        async with httpx.AsyncClient() as client:
            files = {'document': (filename, pdf_file, 'application/pdf')}
            data = {'chat_id': chat_id}
            
            response = await client.post(url, data=data, files=files)
            response.raise_for_status()
            
            return {"success": True, "message": f"PDF Report sent to Telegram (Chat {chat_id})"}
            
    except Exception as e:
        print(f"❌ Telegram Error: {e}")
        error_msg = str(e)
        if "400" in error_msg:
             return {"success": False, "error": f"Telegram API Error (400) for Chat ID {chat_id}. Ensure the user has started the bot (@Doctor_AssistBot). Raw error: {error_msg}"}
        return {"success": False, "error": str(e)}

async def send_telegram_message(chat_id: str, text: str):
    """Send text message to Telegram chat."""
    url = f"{TELEGRAM_BASE_URL}/sendMessage"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json={"chat_id": chat_id, "text": text})
            response.raise_for_status()
            return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
