#!/bin/bash
# Helper script to refresh AWS credentials

echo "🔄 AWS Credentials Refresh Helper"
echo "=================================="
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed."
    echo "   Install it from: https://aws.amazon.com/cli/"
    exit 1
fi

echo "📋 Your current AWS credential status:"
echo ""

# Check current credentials
if aws sts get-caller-identity &> /dev/null; then
    echo "✅ Current AWS CLI credentials are VALID"
    IDENTITY=$(aws sts get-caller-identity)
    echo "$IDENTITY" | python3 -m json.tool 2>/dev/null || echo "$IDENTITY"
    echo ""
    
    echo "🔄 Refreshing credentials..."
    echo ""
    
    # Try to export credentials
    if aws configure export-credentials --format env &> /dev/null; then
        echo "✅ Fresh credentials available!"
        echo ""
        echo "Copy these to your .env file:"
        echo "----------------------------------------"
        aws configure export-credentials --format env | grep -E "^(AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY|AWS_SESSION_TOKEN|AWS_REGION)="
        echo "----------------------------------------"
        echo ""
        echo "💡 Or run this command to update .env automatically:"
        echo "   aws configure export-credentials --format env | grep -E '^(AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY|AWS_SESSION_TOKEN|AWS_REGION)=' >> .env.new && mv .env.new .env"
    else
        echo "⚠️  Could not export credentials automatically"
        echo ""
        echo "📝 Manual steps:"
        echo "1. If using AWS SSO, run: aws sso login"
        echo "2. If using AWS CLI profiles, run: aws configure export-credentials --profile your-profile --format env"
        echo "3. Copy the output to your .env file"
    fi
else
    echo "❌ Current AWS CLI credentials are INVALID or EXPIRED"
    echo ""
    echo "🔧 Try these steps:"
    echo ""
    echo "Option 1: If using AWS SSO"
    echo "   aws sso login"
    echo "   aws configure export-credentials --format env"
    echo ""
    echo "Option 2: If using AWS CLI with profiles"
    echo "   aws configure export-credentials --profile your-profile --format env"
    echo ""
    echo "Option 3: Get permanent credentials"
    echo "   1. Go to: https://console.aws.amazon.com/iam/"
    echo "   2. Users → Your User → Security credentials"
    echo "   3. Create access key → Command Line Interface (CLI)"
    echo "   4. Copy Access Key ID and Secret Access Key"
    echo "   5. Add to .env (no AWS_SESSION_TOKEN needed for permanent keys)"
    echo ""
    echo "Option 4: Use AWS CLI default credentials"
    echo "   aws configure"
    echo "   # Then restart your app (it will use default credential chain)"
fi

echo ""

