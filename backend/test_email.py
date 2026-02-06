
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Manual .env parsing
try:
    if os.path.exists(".env"):
        print("Loading .env file...")
        with open(".env") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"): continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    # Handle comments after value
                    if "#" in v:
                        v = v.split("#", 1)[0].strip()
                    # Handle quotes
                    v = v.strip().strip("'").strip('"')
                    os.environ[k] = v
except Exception as e:
    print(f"Error loading .env: {e}")

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "Medical Assistant")

print(f"SMTP Config: {SMTP_HOST}:{SMTP_PORT}")
print(f"User: {SMTP_USER}")
print(f"Password starts with: {SMTP_PASSWORD[:3]}...")

TO_EMAIL = "mohitadoni01@gmail.com"

try:
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Test Email from Doctor Assistant"
    msg['From'] = f"{EMAIL_FROM_NAME} <{SMTP_USER}>"
    msg['To'] = TO_EMAIL
    
    html = "<h1>It works!</h1><p>This is a test email.</p>"
    msg.attach(MIMEText(html, 'html'))
    
    print(f"Connecting to {SMTP_HOST}...")
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.set_debuglevel(1)
        print("Starting TLS...")
        server.starttls()
        print("Logging in...")
        server.login(SMTP_USER, SMTP_PASSWORD)
        print("Sending message...")
        server.send_message(msg)
        print("✅ SUCCESS! Email sent.")
except Exception as e:
    print(f"❌ ERROR: {e}")
