# 🏥 Medical Appointment System

An AI-powered medical appointment booking system using **FastAPI** (backend) and **React/Vite** (frontend) with the **Model Context Protocol (MCP)** design pattern.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                        │
│                    localhost:5173                              │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTP/JSON
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                              │
│                    localhost:8000                              │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                   Agentic Brain                           │ │
│  │              (OpenAI GPT-4o-mini)                         │ │
│  └───────────────────────┬───────────────────────────────────┘ │
│                          │ Function Calling                    │
│  ┌───────────────────────▼───────────────────────────────────┐ │
│  │                    MCP Tools                              │ │
│  │  • check_availability  • book_appointment                 │ │
│  │  • cancel_appointment  • list_appointments                │ │
│  └───────────────────────┬───────────────────────────────────┘ │
│                          │                                     │
│  ┌───────────────────────▼───────────────────────────────────┐ │
│  │              SQLite Database                              │ │
│  │          (Doctors, Appointments)                          │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- OpenAI API Key

### Backend Setup

```bash
# Create virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run the server
uvicorn main:app --reload
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/doctors` | List all doctors |
| POST | `/doctors` | Create a new doctor |
| POST | `/chat` | AI chat endpoint |

## 🤖 AI Capabilities

The assistant can:
- **Check Availability**: "What times are available tomorrow with a cardiologist?"
- **Book Appointments**: "Book an appointment with Dr. Chen on Friday at 2pm"
- **Cancel Appointments**: "Cancel my appointment #5"
- **List Appointments**: "Show my upcoming appointments"

## 🛠️ Tech Stack

**Backend:**
- FastAPI (Python)
- SQLModel (ORM)
- SQLite (Database)
- OpenAI GPT-4o-mini (LLM)

**Frontend:**
- React 18
- Vite
- Tailwind CSS

## 📁 Project Structure

```
├── backend/
│   ├── main.py           # FastAPI app & endpoints
│   ├── database.py       # SQLModel setup
│   ├── models.py         # Doctor & Appointment models
│   ├── agent.py          # LLM integration
│   └── tools/
│       ├── availability.py  # Check availability tool
│       └── booking.py       # Booking tools
├── frontend/
│   ├── src/
│   │   ├── App.jsx       # Main app
│   │   └── components/
│   │       └── Chat.jsx  # Chat interface
│   ├── index.html
│   └── vite.config.js
└── README.md
```

## 📝 License

MIT License
