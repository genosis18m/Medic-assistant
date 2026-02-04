"""
Medical Appointment System - FastAPI Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Medical Appointment System",
    description="MCP-based medical appointment booking with AI agent",
    version="0.1.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint to verify server is running."""
    return {"status": "healthy", "service": "medical-appointment-api"}


@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint with API info."""
    return {
        "message": "Medical Appointment System API",
        "docs": "/docs",
        "health": "/health"
    }
