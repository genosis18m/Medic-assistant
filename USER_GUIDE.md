# 🏥 Medical Assistant - Complete User Guide

## 📋 Table of Contents
1. [Getting Started](#getting-started)
2. [Patient Features](#patient-features)
3. [Doctor Features](#doctor-features)
4. [Troubleshooting](#troubleshooting)

---

## 🚀 Getting Started

### First Time Setup

**1. Access the Application**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

**2. Choose Your Role**

 **For Patients:**
- Click "Sign In" (top right)
- Create account or login with email
- Automatically directed to Patient interface

**For Doctors:**
- Click "Sign In" then toggle to "Doctor Login"
- Credentials:
  - Email: `doctor12345@gmail.com` OR `adonimohit@gmail.com`
  - Password: `doctor`
- Access full dashboard

---

## 🧑 Patient Features

### Booking an Appointment

**Step 1: Start Conversation**
```
Type: "Show me available doctors"
```
The AI will display all 5 doctors with their specializations.

**Step 2: Select Doctor**
```
Type: "mohit" or "sarah" or "emily" etc.
```
AI shows available time slots for that doctor.

**Step 3: Choose Time**
```
Type: "4 pm" or "10:30 am"
```
AI asks for your name.

**Step 4: Provide Name**
```
Type: "John Doe"
```
AI asks for email.

**Step 5: Provide Email**
```
Type: "john@email.com"
```
AI asks for reason.

**Step 6: State Reason**
```
Type: "fever" or "headache" or "check-up"
```
✅ **Appointment Booked!**

### Quick Actions (Click to Auto-fill)
- 💡 "Show me available doctors"
- 💡 "I need a cardiology appointment"
- 💡 "What times are available tomorrow?"
- 💡 "Book an appointment"

### View Previous Visits
- **Sidebar** (left side) shows all your past appointments
- Each card displays:
  - Doctor name
  - Date & time
  - Reason for visit
  - Status (Confirmed/Cancelled)

### Features You'll See
- ✨ Smooth message animations
- 🎨 Beautiful gradient interface
- 💬 Real-time AI responses
- 📅 Appointment history tracking

---

## 👨‍⚕️ Doctor Features

### Dashboard Overview

**Top Statistics Cards:**
1. **Today's Appointments** - Number of patients scheduled today
2. **This Week** - Total appointments this week
3. **Total Appointments** - All-time count

**Navigation Buttons:**
- 📊 **Reports** - View analytics and statistics
- 📅 **Appointments** - See full appointment list
- 🤖 **AI Assistant** - Access doctor-specific AI features

### Using the Dashboard

**Select Doctor (Dropdown)**
- Switch between different doctors
- View their specific appointments
- Filter data per doctor

**Recent Appointments List**
- Shows last 10 appointments
- Click to view details
- Sorted by date/time

### AI Assistant Features

**Access AI Chat:**
1. Click "AI Assistant" button on dashboard
2. Ask questions like:
   - "How many patients today?"
   - "Show appointments with fever"
   - "Generate my daily report"
   - "Send summary to WhatsApp"

**Report Generation:**
```
Type: "Generate my daily report"
```
AI creates a comprehensive summary of:
- Total appointments
- Common symptoms
- Patient demographics
- Follow-up needs

**WhatsApp Notifications:**
```
Type: "Send summary to WhatsApp"
```
Sends appointment summary to your phone (Twilio integration).

### Appointments Page

**Filters Available:**
- **All** - See everything
- **Today** - Only today's appointments
- **Upcoming** - Future appointments
- **Past** - Historical records

**Each Appointment Shows:**
- Patient name & email
- Date & time
- Reason for visit
- Status
- Symptoms (if provided)

### Reports & Analytics

**Statistics Displayed:**
1. **Total Appointments**
   - Today
   - This Week
   - All Time

2. **Status Breakdown**
   - Confirmed count
   - Cancelled count
   - Completion rate

3. **Daily Summary**
   - Appointments by day
   - Weekly trends

4. **Top Visit Reasons**
   - Most common symptoms
   - Top 5 reasons ranked

**Visual Charts:**
- Bar charts for daily trends
- Pie charts for status distribution
- Timeline view

---

## 🎨 UI Features & Interactions

### Color-Coded System
- **Teal/Blue** - Patient interface (trust, calm)
- **Purple/Blue** - Doctor interface (professionalism)
- **Green badges** - Confirmed appointments
- **Red badges** - Cancelled appointments
- **Yellow badges** - Pending status

### Animations
1. **Message Slide-ins** - Chat messages fade and slide smoothly
2. **Typing Indicator** - Bouncing dots show AI is thinking
3. **Sidebar Stagger** - Appointment cards appear one by one
4. **Button Hover** - Lift effect on hover
5. **Focus Glow** - Input fields glow when focused

### Glassmorphism Effects
- Frosted glass backgrounds
- Blur effects throughout
- Transparent overlays
- Modern, premium feel

---

## 🔧 Troubleshooting

### Frontend Not Loading
```bash
cd frontend
npm install
npm run dev
```
Access: http://localhost:5173

### Backend Not Running
```bash
cd backend
source ../venv/bin/activate
uvicorn main:app --reload --port 8000
```
Access: http://localhost:8000/health

### Email Confirmations Not Sending

**Issue:** Gmail rejecting password

**Fix:**
1. Go to: https://myaccount.google.com/apppasswords
2. Sign in: mohitadoni01@gmail.com
3. Create app password: "Medical Assistant"
4. Copy 16-character code
5. Edit `backend/.env`:
```
SMTP_PASSWORD=your-new-password-here
```
6. Restart backend

### Bookings Not Saving

**Check:**
1. Backend running? → http://localhost:8000/health
2. Database connected? → Check `backend/.env` for `DATABASE_URL`
3. View logs: `tail -f /tmp/backend.log`

### Animations Not Working

**Fix:**
```bash
cd frontend
npm install framer-motion react-markdown
```

---

## 📊 Available Doctors

| ID | Name | Specialization |
|----|------|----------------|
| 1 | Dr. Sarah Johnson | General Practice |
| 2 | Dr. Michael Chen | Cardiology |
| 3 | Dr. Emily Williams | Dermatology |
| 4 | Dr. James Brown | Neurology |
| 5 | Dr. Mohit Adoni | General Practice |

**Hours:** All doctors available 9:00 AM - 5:00 PM
**Slot Duration:** 30 minutes

---

## 🎯 Quick Tips

### For Best Experience:
1. ✅ Use Chrome or Firefox
2. ✅ Enable JavaScript
3. ✅ Clear cache if UI looks weird
4. ✅ Use descriptive reasons ("fever and cough" not just "sick")
5. ✅ Check previous visits before rebooking

### Keyboard Shortcuts:
- **Enter** - Send message
- **Shift + Enter** - New line in message
- **Esc** - Clear input

### Smart AI Features:
- Understands casual language ("mohit" = Dr. Mohit Adoni)
- Remembers conversation context
- Asks follow-up questions
- Validates all inputs

---

## 🆘 Need Help?

**Common Questions:**

**Q: Can I cancel an appointment?**
A: Currently in development. Contact doctor directly.

**Q: How do I view my appointment details?**
A: Check the sidebar on Patient page.

**Q: Can I reschedule?**
A: Book a new appointment with preferred time.

**Q: Where's my confirmation email?**
A: Make sure Gmail App Password is set in backend/.env

**Q: Can I book for someone else?**
A: Yes, use their name and email when asked.

---

## 🔐 Security & Privacy

- ✅ All appointments encrypted in database
- ✅ Email addresses protected
- ✅ Clerk authentication for patients
- ✅ Role-based access control
- ✅ HTTPS ready for production

---

## 📱 Mobile Support

Currently optimized for desktop. Mobile responsive design coming soon!

---

**Version:** 1.0.0  
**Last Updated:** February 2026  
**Support:** Check GitHub issues or backend logs

🎉 **Enjoy your Medical Assistant experience!**
