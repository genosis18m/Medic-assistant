
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

print("Importing tools.doctors...")
try:
    from tools.doctors import list_doctors
    print("Success importing tools.doctors")
    print("Testing list_doctors...")
    print(list_doctors())
except Exception as e:
    print(f"Error importing/running list_doctors: {e}")
    import traceback
    traceback.print_exc()

print("\nImporting tools.availability...")
try:
    from tools.availability import check_availability
    print("Success importing tools.availability")
    print("Testing check_availability for docter 4 on 2026-02-07...")
    print(check_availability(check_date="2026-02-07", doctor_id=4))
except Exception as e:
    print(f"Error importing/running availability: {e}")
    import traceback
    traceback.print_exc()
