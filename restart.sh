#!/bin/bash
# Emergency restart script

echo "🔄 Emergency Restart - Medical Assistant"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Kill all processes
echo "1. Killing old processes..."
killall -9 node 2>/dev/null
lsof -ti :5173 | xargs kill -9 2>/dev/null
lsof -ti :8000 | xargs kill -9 2>/dev/null
sleep 2

# Start backend
echo "2. Starting backend..."
cd /home/mohit-adoni/Doctor-Assistant/backend
source ../venv/bin/activate
uvicorn main:app --reload --port 8000 > /tmp/backend_restart.log 2>&1 &
sleep 3

# Start frontend
echo "3. Starting frontend..."
cd /home/mohit-adoni/Doctor-Assistant/frontend
npm run dev > /tmp/frontend_restart.log 2>&1 &
sleep 5

# Check status
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4. Checking services..."

if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend: http://localhost:8000"
else
    echo "❌ Backend: FAILED"
fi

if curl -s http://localhost:5173 > /dev/null; then
    echo "✅ Frontend: http://localhost:5173"
else
    echo "❌ Frontend: FAILED"
    echo "Check logs: tail -f /tmp/frontend_restart.log"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
