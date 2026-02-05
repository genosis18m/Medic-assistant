# 🏥 Medical Appointment System - Agentic AI with MCP

An AI-powered medical appointment booking and reporting system using **FastAPI**, **React/Vite**, and the **Model Context Protocol (MCP)** design pattern. Built for the Full-Stack Developer Intern Assignment.

## ✨ Features

### 🧑 Patient Features
- **Natural Language Booking**: "Book an appointment with Dr. Chen tomorrow at 2pm"
- **Availability Checking**: "What times are available with a cardiologist this Friday?"
- **Multi-turn Conversations**: Context is maintained between prompts
- **Email Confirmations**: Automatic booking confirmations (Gmail SMTP)
- **Calendar Integration**: Google Calendar events created automatically

### 👨‍⚕️ Doctor Features
- **AI-Powered Queries**: "How many patients visited yesterday?" or "Show patients with fever"
- **Summary Reports**: Daily/weekly appointment summaries
- **Slack Notifications**: Send reports directly to Slack
- **Dashboard View**: Visual stats and quick actions

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend (React/Vite)                       │
│                  localhost:5173                                 │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│   │ Role Selector│  │   Chat UI    │  │   Dashboard  │         │
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
│  │                    MCP Tools                              │ │
│  │  Patient Tools:              Doctor Tools:                │ │
│  │  • check_availability        • get_appointment_stats      │ │
│  │  • book_appointment          • get_patient_stats          │ │
│  │  • cancel_appointment        • generate_summary_report    │ │
│  │  • list_appointments         • send_slack_notification    │ │
│  └───────────────────────┬───────────────────────────────────┘ │
│                          │                                     │
│  ┌───────────────────────▼───────────────────────────────────┐ │
│  │              External Services                            │ │
│  │  📅 Google Calendar  |  📧 Gmail SMTP  |  💬 Slack        │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
             ┌────────────────────────┐
             │   PostgreSQL / SQLite  │
             │   (Doctors, Patients,  │
             │    Appointments)       │
             └────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- Groq API Key (free at [console.groq.com](https://console.groq.com))
- PostgreSQL (optional, SQLite used by default)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Run server
uvicorn main:app --reload
```

Backend available at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend available at `http://localhost:5173`

## 🔧 Environment Variables

```bash
# Required
GROQ_API_KEY=your_groq_api_key

# Database (optional - defaults to SQLite)
DATABASE_URL=postgresql://user:pass@localhost:5432/medical_db

# Google Calendar (optional)
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Slack (optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx/yyy/zzz
```

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/doctors` | List all doctors |
| POST | `/doctors` | Create a new doctor |
| POST | `/chat` | AI chat endpoint (supports role param) |
| POST | `/doctor/report` | Generate doctor report |
| GET | `/appointments` | List appointments with filters |
| GET | `/stats` | Get appointment statistics |
| POST | `/notifications/test-slack` | Test Slack webhook |

## 💬 Sample Prompts

### Patient Mode
```
"I want to book an appointment with Dr. Chen tomorrow morning"
"Show me available times with a cardiologist"
"Cancel my appointment #3"
"What appointments do I have scheduled?"
```

### Doctor Mode
```
"How many patients visited yesterday?"
"How many appointments do I have today?"
"Show me patients with fever this week"
"Generate my daily report and send to Slack"
```

## 🎯 Multi-Turn Conversation Example

```
Patient: "Check Dr. Chen's availability for Friday"
AI: "Dr. Michael Chen (Cardiology) has these slots available on Friday..."

Patient: "Book the 3 PM slot"
AI: "I'll book that for you. What's your name and email?"

Patient: "John Doe, john@example.com"
AI: "✅ Appointment confirmed! You'll receive an email confirmation..."
```

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, Vite, Tailwind CSS |
| Backend | FastAPI, Python 3.12 |
| Database | PostgreSQL / SQLite |
| LLM | Groq (Llama 3.1 8B) |
| Calendar | Google Calendar API |
| Email | Gmail SMTP / SendGrid |
| Notifications | Slack Webhooks |

## 📁 Project Structure

```
├── backend/
│   ├── main.py              # FastAPI app & endpoints
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLModel models
│   ├── agent.py             # Agentic brain with Groq
│   ├── services/
│   │   ├── google_calendar.py
│   │   ├── email_service.py
│   │   └── slack_service.py
│   └── tools/
│       ├── availability.py  # Check availability tool
│       ├── booking.py       # Booking tools
│       └── doctor_reports.py # Doctor reporting tools
│
├── frontend/
│   └── src/
│       ├── App.jsx
│       └── components/
│           ├── Chat.jsx          # Role-aware chat interface
│           ├── RoleSelector.jsx  # Patient/Doctor selection
│           └── DoctorDashboard.jsx
└── README.md
```

## 🏆 Bonus Features Implemented

- [x] Role-based UI (Patient vs Doctor views)
- [x] Prompt history tracking (stored in database)
- [x] Multi-notification channels (Email + Slack)
- [x] Dashboard with visual stats
- [x] Multi-turn conversation support

## 📝 License

MIT License
