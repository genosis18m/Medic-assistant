# 🏥 Medical Appointment System - Agentic AI with MCP

An AI-powered medical appointment booking and reporting system using **FastAPI**, **React/Vite**, and the **Model Context Protocol (MCP)** design pattern. Built for the Full-Stack Developer Intern Assignment.

## ✨ Features

### 🧑 Patient Features
- **Natural Language Booking**: "Book an appointment with Dr. Chen tomorrow at 2pm"
- **Availability Checking**: "What times are available with a cardiologist this Friday?"
- **Multi-turn Conversations**: Context is maintained between prompts
- **Email Confirmations**: Automatic booking confirmations (Gmail SMTP)
- **Calendar Integration**: Google Calendar events created automatically
- **Visit History Tracking**: All visits saved with reasons and symptoms

### 👨‍⚕️ Doctor Features
- **AI-Powered Queries**: "How many patients visited yesterday?" or "Show patients with fever"
- **Summary Reports**: Daily/weekly appointment summaries
- **Slack Notifications**: Send reports directly to Slack
- **WhatsApp Notifications**: Send reports via WhatsApp (Twilio)
- **Patient History**: View complete visit history for any patient
- **Prescriptions**: Add medications per visit
- **PDF Reports**: Generate downloadable patient reports
- **Dashboard View**: Visual stats and quick actions

## 🔐 Login Credentials

### Doctor Access
| Email | Password | Notes |
|-------|----------|-------|
| `doctor@clinic.com` | `password` | **Test Account** (Bypasses Clerk) |

 ## Can link personal accoounts too for each doctor:
| `doctor12345@gmail.com` |  | Dr. Sarah Johnson |
| `adonimohit@gmail.com` | | Dr. Mohit Adoni |

### Patient Access
| Email | Password | Notes |
|-------|----------|-------|
| `patient@clinic.com` | `password` | **Test Account** (Click "Use Test Patient Account") |
| Any Email | (Clerk) | Sign up required |

> **Note**: For "Test Accounts", no sign-up is required. Just click the link/button on the login page.

## 🔧 13 MCP Tools

### Patient Tools (4)
| Tool | Description |
|------|-------------|
| `check_availability` | Find available appointment slots |
| `book_appointment` | Book with email + calendar + creates visit record |
| `cancel_appointment` | Cancel existing appointments |
| `list_appointments` | View scheduled appointments |

### Doctor Tools (5)
| Tool | Description |
|------|-------------|
| `get_appointment_stats` | Query appointment statistics |
| `get_patient_stats` | Find patients by symptoms/diagnosis |
| `generate_summary_report` | Create daily/weekly reports |
| `send_slack_notification` | Send reports to Slack |
| `send_report_to_whatsapp` | Send reports via WhatsApp |

### Patient History Tools (4)
| Tool | Description |
|------|-------------|
| `get_patient_history` | View complete visit history |
| `add_visit_notes` | Add diagnosis and doctor notes |
| `add_prescription` | Add medications per visit |
| `generate_patient_report` | Generate PDF patient report |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend (React/Vite)                       │
│                  localhost:5173                                 │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│   │ Role Selector│  │   Chat UI    │  │   Dashboard  │         │
│   │(Patient/Doc) │  │(Multi-turn)  │  │(Doctor Only) │         │
│   └──────────────┘  └──────────────┘  └──────────────┘         │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP/JSON
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                              │
│                    localhost:8000                               │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              Agentic Brain (Groq LLM)                     │ │
│  │         Role-aware prompts + Multi-turn context           │ │
│  └───────────────────────┬───────────────────────────────────┘ │
│                          │ Function Calling                    │
│  ┌───────────────────────▼───────────────────────────────────┐ │
│  │                  13 MCP Tools                             │ │
│  │  Patient(4) + Doctor(5) + History(4)                      │ │
│  └───────────────────────┬───────────────────────────────────┘ │
│                          │                                     │
│  ┌───────────────────────▼───────────────────────────────────┐ │
│  │              External Services                            │ │
│  │  📅 Google Calendar | 📧 Gmail | 💬 Slack | 📱 WhatsApp   │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
             ┌────────────────────────┐
             │   Neon PostgreSQL      │
             │   (6 Tables)           │
             └────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- Groq API Key (free at [console.groq.com](https://console.groq.com))

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your GROQ_API_KEY to .env
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## 🔧 Environment Variables

```bash
# Required
GROQ_API_KEY=your_groq_api_key

# Database (Neon PostgreSQL)
DATABASE_URL=postgresql://user:pass@host/dbname?sslmode=require

# Google Calendar
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret

# Email (Gmail SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx

# WhatsApp (Twilio)
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Clerk Auth (Frontend)
VITE_CLERK_PUBLISHABLE_KEY=pk_test_xxx
```

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/doctors` | List all doctors |
| POST | `/chat` | AI chat (role: patient/doctor) |
| POST | `/doctor/report` | Generate doctor report |
| GET | `/appointments` | List appointments |
| GET | `/stats` | Get statistics |

## 💬 Sample Prompts

### Patient Mode
```
"I want to book an appointment with Dr. Chen tomorrow morning"
"Show me available times with a cardiologist"
"Cancel my appointment #3"
```

### Doctor Mode
```
"How many patients visited yesterday?"
"How many appointments do I have today?"
"Show me patients with fever this week"
"Generate my daily report and send to WhatsApp"
```

## 🎯 Multi-Turn Conversation

```
Patient: "Check Dr. Chen's availability for Friday"
AI: "Dr. Michael Chen has these slots available..."

Patient: "Book the 3 PM slot"
AI: "I'll book that. What's your name and email?"

Patient: "John Doe, john@example.com"
AI: "What's the reason for your visit?"

Patient: "Fever"
AI: "✅ Appointment confirmed! Email and calendar invite sent."
```

## Database Schema

| Table | Description |
|-------|-------------|
| `doctor` | Doctors with specializations |
| `patient` | Patient information |
| `appointment` | Booked appointments |
| `visit` | Visit history with symptoms/diagnosis |
| `prescription` | Medications per visit |
| `prompthistory` | Chat history tracking |

## 🏆 Bonus Features

- [x] Role-based UI (Patient vs Doctor)
- [x] Prompt history tracking
- [x] Multiple notification channels (Email + Slack + WhatsApp)
- [x] Dashboard with visual stats
- [x] Multi-turn conversation support
- [x] Clerk authentication
- [x] Patient history tracking
- [x] Prescription management
- [x] PDF report generation

## 📝 License

MIT License
