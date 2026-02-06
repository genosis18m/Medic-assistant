#!/bin/bash

# Navigate to project root
cd /home/mohit-adoni/Doctor-Assistant

# Activate virtual environment
source venv/bin/activate

# Navigate to backend directory to ensure relative imports work (e.g. 'from database import...')
cd backend

# Start the server
echo "🚀 Starting Medical Assistant Backend on port 8000..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000
