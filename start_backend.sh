#!/bin/bash
# Start the FastAPI backend server

cd "$(dirname "$0")"

echo "🚀 Starting AWS Bedrock Code Review Agent - Backend API"
echo "======================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing backend dependencies..."
pip install -r backend/requirements.txt -q
pip install -r requirements.txt -q

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "   Please create .env file with AWS credentials"
    echo "   See .env.example for format"
    exit 1
fi

echo ""
echo "✅ Starting backend server on http://localhost:8000"
echo "   API docs available at http://localhost:8000/docs"
echo ""

# Start the server
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

