# 🏥 Medical Assistant AI - User Guide

Welcome to the **Medical Assistant AI System**, a powerful tool designed to streamline patient management and scheduling for doctors. This guide covers all features for both **Doctors** and **Patients**.

---

## 🚀 Quick Start (Doctor Mode)

### 1. Accessing the Dashboard
- Navigate to `/doctor` or simply log in as a doctor.
- **Default Login:** Dr. Mohit Adoni (General)

### 2. Switching Doctor Context
The system supports multi-doctor clinics. To switch your active view:
1.  Look for the **"Viewing as:"** dropdown in the top purple header of the chat.
2.  Select a doctor (e.g., *Dr. Sarah Johnson*).
3.  The AI immediately switches context. All reports and schedules will now reflect *that* doctor's data.

### 3. Using the AI Assistant
The chat interface is your command center. Try these commands:
- **"Today's Schedule"**: Shows confirmed appointments for the current day.
- **"Tomorrow's Schedule"**: Previews the next day's bookings.
- **"Weekly Report"**: Generates a summary of patient load for the week.
- **"Patient Stats"**: Displays key metrics (Total patients, cancellations, etc.).

> **💡 Tip:** Use the **Quick Action Chips** above the input bar for one-click commands!

---

## 📅 Managing Appointments

### For Doctors
- The **Appointments** tab shows a traditional calendar view.
- Click on any slot to view patient details.
- Currently, the Calendar is read-only for historical accuracy; use the AI to query availability.

### For Patients
- Navigate to `/patient` to access the booking portal.
- Select a doctor and specialization.
- Choose a date and time slot.
- **Note:** The innovative "Date Slider" allows you to pick slots for Today, Tomorrow, or the Day After.

---

## 🎨 Interface Features

### Glassmorphism UI
- **Panels:** Semantic ease-of-use with see-through glass panels.
- **Focus:** Inputs glow when active (`Teal` for primary actions).
- **Feedback:** Buttons pulse slightly on click for tactile feel.

### Color Coding
- **Teal (Green/Blue):** Primary actions, Confirmations, Trust.
- **Coral (Red/Pink):** Alerts, Cancellations, Urgent items.
- **Slate (Dark Grey):** Backgrounds, Neutral readability.

---

## 🔧 Troubleshooting

### "Failed to Fetch" / Backend Error
- **Cause:** The backend server (`uvicorn`) is stopped.
- **Fix:** Restart the backend terminal or ask the AI to "Restart Backend".

### "Wrong Doctor Info"
- **Cause:** You might be viewing the wrong context.
- **Fix:** Check the **"Viewing as:"** dropdown in the chat header. Switch to the correct name.

### White Screen on Load
- **Cause:** Browser cache or React rendering error.
- **Fix:** Hard refresh the page (`Ctrl + F5` or `Cmd + Shift + R`).

---

## 🎹 Keyboard Shortcuts

- **`Enter`**: Send message
- **`Shift + Enter`**: New line in chat
- **`Esc`**: Clear input focus

---

*System Version: 2.1.0 | © 2026 Medical Assistant AI*
