from services.telegram_service import generate_pdf_report
import os

print("Testing PDF Generation...")
pdf = generate_pdf_report("Dr. Test", [{"time": "10:00", "patient_name": "John", "reason": "Fever"}], "2024-01-01")
print(f"Generated PDF size: {len(pdf.getvalue())} bytes")
print("Success!")
