#!/bin/bash
# Start both backend and frontend servers

cd "$(dirname "$0")"

echo "🚀 Starting AWS Bedrock Code Review Agent"
echo "=========================================="
echo ""

# Start backend in background
echo "Starting backend server..."
./start_backend.sh &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start frontend
echo ""
echo "Starting frontend server..."
./start_frontend.sh &
FRONTEND_PID=$!

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

echo ""
echo "✅ Both servers are starting..."
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for both processes
wait

