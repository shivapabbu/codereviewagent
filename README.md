# 🔍 AWS Bedrock Code Review Agent

A full-featured code review agent powered by AWS Bedrock and Claude 3, featuring both a CLI backend and a Streamlit web UI. Analyze code files or diffs, detect issues, get suggestions, and automatically apply fixes.

## 🎯 Features

- **Code Analysis**: Analyze individual files or diff files
- **Issue Detection**: Identifies bugs, style issues, documentation gaps, performance problems, and security concerns
- **Auto-Fix Suggestions**: Get code suggestions in GitHub-style format
- **Apply Fixes**: One-click apply fixes directly to your code files
- **Web UI**: Beautiful Streamlit interface for easy interaction
- **CLI Tool**: Command-line interface for automation
- **Results Storage**: Save review results as JSON files

## 📋 Prerequisites

1. **AWS Account** with Bedrock access enabled
   - Go to AWS Console → Bedrock → Model Access
   - Request access to Claude 3 Sonnet model
2. **Python 3.8+**
3. **AWS Credentials** (Access Key ID and Secret Access Key)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

**Note**: Make sure `.env` is in your `.gitignore` to keep credentials secure!

### 3. Run the Web UI

```bash
streamlit run app.py
```

The UI will open in your browser at `http://localhost:8501`

### 4. Or Use the CLI

```bash
python review_agent.py
```

Then enter the path to your file or diff when prompted.

## 📖 Usage

### Web UI (Streamlit)

1. **Upload a File**: Use the "File Upload" tab to upload a code file or diff
2. **Paste Code**: Use the "Code Input" tab to paste code directly
3. **View Results**: Check the "Review Results" tab for:
   - Summary and overall score
   - Detailed issues with severity levels
   - Missing docstrings
   - Apply fixes with one click
4. **Download Results**: Download review results as JSON

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
├── review_agent.py      # Backend CLI tool
├── app.py               # Streamlit web UI
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (create this)
├── .env.example         # Example env file
├── results/             # Review results storage
└── README.md            # This file
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

