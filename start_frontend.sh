#!/bin/bash
# Start the Next.js frontend server

cd "$(dirname "$0")/frontend"

echo "🚀 Starting AWS Bedrock Code Review Agent - Frontend"
echo "=================================================="
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "⚠️  Warning: Backend API not detected at http://localhost:8000"
    echo "   Please start the backend first: ./start_backend.sh"
    echo ""
fi

echo "✅ Starting frontend server on http://localhost:3000"
echo ""

# Start Next.js dev server
npm run dev

