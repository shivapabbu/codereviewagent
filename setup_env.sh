#!/bin/bash
# Setup script for AWS Bedrock Code Review Agent

echo "🔍 AWS Bedrock Code Review Agent - Setup"
echo "========================================"
echo ""

# Check if .env exists
if [ -f .env ]; then
    echo "⚠️  .env file already exists. Backing up to .env.backup"
    cp .env .env.backup
fi

# Create .env file
echo "Creating .env file..."
cat > .env << EOF
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
EOF

echo "✅ .env file created!"
echo ""
echo "📝 Please edit .env file and add your AWS credentials:"
echo "   - AWS_ACCESS_KEY_ID"
echo "   - AWS_SECRET_ACCESS_KEY"
echo "   - AWS_REGION (if different from us-east-1)"
echo ""
echo "🚀 Next steps:"
echo "   1. Edit .env with your credentials"
echo "   2. Install dependencies: pip install -r requirements.txt"
echo "   3. Run the UI: streamlit run app.py"
echo "   4. Or use CLI: python review_agent.py"
echo ""

