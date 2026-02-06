import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Explicitly set credentials for debugging
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "momoochan.ofc@gmail.com"
SMTP_PASSWORD = "bdvxejjqmdnuoxrp"
EMAIL_FROM_NAME = "Medical Assistant Debug"

def test_email():
    print(f"Testing email to: mohitadoni18@gmail.com")
    print(f"Using Account: {SMTP_USER}")
    
    try:
        msg = MIMEMultipart()
        msg['Subject'] = "Debug Email Test"
        msg['From'] = f"{EMAIL_FROM_NAME} <{SMTP_USER}>"
        msg['To'] = "mohitadoni18@gmail.com"
        
        msg.attach(MIMEText("This is a test email from the debugging script. If you see this, SMTP is working.", 'plain'))
        
        print("Connecting to SMTP server...")
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.set_debuglevel(1)  # Enable debug output
            server.starttls()
            print("Logging in...")
            server.login(SMTP_USER, SMTP_PASSWORD)
            print("Sending message...")
            server.send_message(msg)
            
        print("✅ Email sent successfully!")
        
    except Exception as e:
        print(f"❌ Failed to send: {e}")

if __name__ == "__main__":
    test_email()
