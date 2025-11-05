# 🔍 AWS Bedrock Code Review Agent

A full-featured code review agent powered by AWS Bedrock and Claude 3, featuring a modern React/Next.js frontend dashboard and FastAPI backend. Analyze code files or diffs, detect issues, get suggestions, and automatically apply fixes.

## 🎯 Features

- **Code Analysis**: Analyze individual files or diff files
- **Issue Detection**: Identifies bugs, style issues, documentation gaps, performance problems, and security concerns
- **Auto-Fix Suggestions**: Get code suggestions in GitHub-style format
- **Apply Fixes**: One-click apply fixes directly to your code files
- **Modern Web UI**: Beautiful React/Next.js dashboard with Tailwind CSS
- **REST API**: FastAPI backend for easy integration
- **CLI Tool**: Command-line interface for automation
- **Results Storage**: Save review results as JSON files

## 📋 Prerequisites

1. **AWS Account** with Bedrock access enabled
   - Go to AWS Console → Bedrock → Model Access
   - Request access to Claude 3 Sonnet model
2. **Python 3.8+** (for backend)
3. **Node.js 18+** (for frontend)
4. **AWS Credentials** (Access Key ID and Secret Access Key)

## 🚀 Quick Start

### 1. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
# For temporary credentials (ASIA prefix), also add:
# AWS_SESSION_TOKEN=your_session_token
MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

**Note**: Make sure `.env` is in your `.gitignore` to keep credentials secure!

### 2. Start the Application

**Option A: Start both servers together (Recommended)**

```bash
./start.sh
```

**Option B: Start servers separately**

```bash
# Terminal 1: Start backend
./start_backend.sh

# Terminal 2: Start frontend
./start_frontend.sh
```

The frontend will open in your browser at `http://localhost:3000`
The backend API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

### 3. Or Use the CLI

```bash
python review_agent.py
```

Then enter the path to your file or diff when prompted.

## 📖 Usage

### Web UI (Next.js Dashboard)

1. **Upload a File**: Use the "File Upload" tab to upload a code file or diff (drag & drop supported)
2. **Paste Code**: Use the "Code Input" tab to paste code directly
3. **View Results**: The dashboard shows:
   - Summary and overall score
   - Detailed issues with severity levels (High/Medium/Low)
   - Missing docstrings with suggestions
   - Apply fixes with one click
   - Syntax-highlighted code suggestions
4. **Download Results**: Download review results as JSON

### REST API

The backend exposes a REST API at `http://localhost:8000`:

- `POST /api/review/code` - Review code from text
- `POST /api/review/file` - Review uploaded file
- `POST /api/review/file-path` - Review file from server path
- `POST /api/fix/apply` - Apply a fix to a file
- `GET /api/results` - Get recent review results
- `GET /docs` - Interactive API documentation

See `http://localhost:8000/docs` for full API documentation.

### CLI Tool

```bash
python review_agent.py
Enter file path or diff file: src/example.py
```

The CLI will:
- Analyze the file
- Display formatted results in the terminal
- Save results to `results/` directory

### Analyzing Diffs

You can analyze diff files (`.diff` or `.patch`):

```bash
python review_agent.py
Enter file path or diff file: changes.diff
```

Or use git to generate diffs:

```bash
git diff > my_changes.diff
python review_agent.py
# Then enter: my_changes.diff
```

## 🏗️ Project Structure

```
codereviewagent/
├── backend/
│   ├── main.py          # FastAPI backend server
│   └── requirements.txt # Backend Python dependencies
├── frontend/
│   ├── app/             # Next.js app directory
│   │   ├── components/  # React components
│   │   ├── lib/         # API client utilities
│   │   └── page.tsx     # Main dashboard page
│   ├── package.json     # Frontend dependencies
│   └── tailwind.config.js
├── review_agent.py      # Backend CLI tool (core logic)
├── requirements.txt     # Python dependencies (shared)
├── .env                 # Environment variables (create this)
├── .env.example         # Example env file
├── results/             # Review results storage
├── start.sh             # Start both servers
├── start_backend.sh     # Start backend only
├── start_frontend.sh    # Start frontend only
└── README.md            # This file
```

## 🔧 Development Setup

### Backend Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install backend dependencies
pip install -r backend/requirements.txt
pip install -r requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
```

### Running in Development

```bash
# Backend (with auto-reload)
cd backend
uvicorn main:app --reload

# Frontend (with hot reload)
cd frontend
npm run dev
```

## 🔧 Configuration

### Available Models

You can change the model in your `.env` file:

- `anthropic.claude-3-sonnet-20240229-v1:0` (default)
- `anthropic.claude-3-haiku-20240307-v1:0` (faster, cheaper)
- `anthropic.claude-3-opus-20240229-v1:0` (most capable)

### AWS Regions

Supported regions include:
- `us-east-1` (default)
- `us-west-2`
- `eu-west-1`
- `ap-southeast-1`

Check AWS Bedrock documentation for full list of supported regions.

## 🎨 Features in Detail

### Issue Detection

The agent detects:
- **Bugs**: Logical errors and potential runtime issues
- **Style Issues**: Code formatting and PEP 8 compliance
- **Documentation**: Missing docstrings and comments
- **Performance**: Inefficient code patterns
- **Security**: Vulnerabilities and security concerns

### Auto-Fix

When issues are detected, you can:
1. View the suggested fix in the UI
2. Click "Apply Fix" to automatically update the file
3. A backup is created (`.backup` extension) before applying changes

### Results Format

Results are saved as JSON with:
```json
{
  "summary": "Brief summary",
  "issues": [
    {
      "type": "bug|style|documentation|performance|security",
      "severity": "high|medium|low",
      "line": 42,
      "message": "Description",
      "suggestion": "Code fix"
    }
  ],
  "missing_docstrings": [...],
  "overall_score": 8
}
```

## 🐛 Troubleshooting

### "Bedrock client not initialized"

- Check your AWS credentials in `.env`
- Verify AWS_REGION is correct
- Ensure Bedrock is enabled in your AWS account

### "Model access denied"

- Request model access in AWS Console → Bedrock → Model Access
- Wait for approval (usually instant for Claude models)

### "No content in response"

- Check your AWS credentials are valid
- Verify the model ID is correct
- Check AWS service quotas

## 📝 Example

Analyze a Python file:

```python
# example.py
def process_data(data):
    result = []
    for x in data:
        result.append(x*2)
    return result
```

**Review Output:**
- ⚠️ Missing docstring for `process_data`
- ⚠️ Style: Space around operator (`x*2` → `x * 2`)
- Overall Score: 6/10

**Suggested Fix:**
```python
def process_data(data):
    """Double each element in the given data list."""
    result = []
    for x in data:
        result.append(x * 2)
    return result
```

## 🔒 Security

- **Never commit `.env` file** - it contains sensitive credentials
- Use IAM roles with least privilege access
- Consider using AWS IAM roles instead of access keys when deploying
- Review code before applying auto-fixes

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- AWS Bedrock for the AI infrastructure
- Anthropic for Claude models
- Streamlit for the UI framework

---

**Happy Code Reviewing! 🚀**

