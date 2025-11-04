# 🚀 Quick Start Guide

Get up and running with the AWS Bedrock Code Review Agent in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Set Up AWS Credentials

### Option A: Use the Setup Script (Recommended)

```bash
./setup_env.sh
```

Then edit `.env` and add your AWS credentials.

### Option B: Manual Setup

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```bash
   AWS_REGION=us-east-1
   AWS_ACCESS_KEY_ID=your_actual_access_key
   AWS_SECRET_ACCESS_KEY=your_actual_secret_key
   MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
   ```

## Step 3: Enable Bedrock Access

1. Go to [AWS Console → Bedrock](https://console.aws.amazon.com/bedrock/)
2. Click "Model access" in the left sidebar
3. Find "Claude 3 Sonnet" and click "Request model access"
4. Wait for approval (usually instant)

## Step 4: Run the Application

### Web UI (Recommended)

```bash
streamlit run app.py
```

Open your browser to `http://localhost:8501`

### CLI Tool

```bash
python review_agent.py
```

When prompted, enter a file path (e.g., `test_example.py`)

## Step 5: Test It Out

Try analyzing the included test file:

```bash
python review_agent.py
# Enter: test_example.py
```

Or use the web UI to upload `test_example.py`

## ✅ You're Ready!

You should see:
- Code analysis results
- Issue detection
- Suggestions for improvements
- Ability to apply fixes (in UI)

## 🆘 Troubleshooting

**"Bedrock client not initialized"**
- Check your `.env` file has correct credentials
- Verify AWS_REGION is correct

**"Model access denied"**
- Request model access in AWS Console (Step 3)

**"No module named 'streamlit'"**
- Run: `pip install -r requirements.txt`

---

Need help? Check the full [README.md](README.md) for detailed documentation.

