# 🚀 Setup Guide - React/Next.js Frontend

## Quick Start

### 1. Install Prerequisites

**Backend (Python):**
```bash
# Python 3.8+ required
python3 --version

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
pip install -r requirements.txt
```

**Frontend (Node.js):**
```bash
# Node.js 18+ required
node --version

# Install dependencies
cd frontend
npm install
cd ..
```

### 2. Configure AWS Credentials

Create `.env` file in project root:

```bash
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
# For temporary credentials (ASIA prefix):
# AWS_SESSION_TOKEN=your_session_token
MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

### 3. Start the Application

**Easy Way (Both Servers):**
```bash
./start.sh
```

**Manual Way:**
```bash
# Terminal 1: Backend
./start_backend.sh

# Terminal 2: Frontend  
./start_frontend.sh
```

### 4. Access the Application

- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Troubleshooting

### Backend won't start

1. Check Python version: `python3 --version` (needs 3.8+)
2. Verify virtual environment is activated
3. Check `.env` file exists and has correct credentials
4. Install dependencies: `pip install -r backend/requirements.txt`

### Frontend won't start

1. Check Node.js version: `node --version` (needs 18+)
2. Install dependencies: `cd frontend && npm install`
3. Check if backend is running (frontend needs backend API)

### API Connection Issues

1. Verify backend is running on port 8000
2. Check CORS settings in `backend/main.py`
3. Verify API URL in `frontend/app/lib/api.ts`

### AWS Credentials Issues

See `CREDENTIALS_TROUBLESHOOTING.md` for detailed help.

## Development

### Backend Development

```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Frontend Development

```bash
cd frontend
npm run dev
```

Both servers support hot reload during development.

## Production Build

### Backend

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm run build
npm start
```

## Architecture

```
┌─────────────────┐
│  Next.js UI     │  http://localhost:3000
│  (React/TS)     │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│  FastAPI Backend │  http://localhost:8000
│  (Python)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AWS Bedrock    │
│  (Claude 3)     │
└─────────────────┘
```

## Next Steps

1. ✅ Start both servers
2. ✅ Open http://localhost:3000
3. ✅ Upload a code file or paste code
4. ✅ View review results
5. ✅ Apply fixes if needed

Happy coding! 🎉

