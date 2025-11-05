# 🔧 AWS Credentials Troubleshooting Guide

## Common Error: "UnrecognizedClientException: The security token included in the request is invalid"

This error means your AWS credentials are either:
- Invalid or expired
- **Temporary credentials (ASIA prefix) missing AWS_SESSION_TOKEN** ← Most common!
- Incorrectly formatted in the `.env` file
- Missing quotes or have extra quotes

## 🔑 Two Types of AWS Credentials

### 1. Permanent Credentials (AKIA prefix)
- Start with `AKIA...`
- Don't expire (unless manually rotated)
- Only need Access Key ID and Secret Access Key

### 2. Temporary Credentials (ASIA prefix)
- Start with `ASIA...`
- **REQUIRE AWS_SESSION_TOKEN**
- Expire after a few hours
- Used when assuming roles or using AWS SSO

## ✅ Correct .env Format

**WRONG (with quotes):**
```bash
AWS_ACCESS_KEY_ID="AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
```

**CORRECT - Permanent Credentials (AKIA):**
```bash
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

**CORRECT - Temporary Credentials (ASIA):**
```bash
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=ASIAVRUVSXEXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_SESSION_TOKEN=IQoJb3JpZ2luX2Vj...  # ← REQUIRED for ASIA credentials!
MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

⚠️ **If your Access Key starts with `ASIA`, you MUST include `AWS_SESSION_TOKEN`!**

## 🔍 Quick Checks

1. **No quotes around values** - The `.env` parser will include quotes as part of the value
2. **No spaces around `=`** - Use `KEY=value` not `KEY = value`
3. **No trailing spaces** - Make sure values don't end with spaces
4. **Valid credentials** - Ensure your AWS Access Key ID and Secret Access Key are still valid

## 🧪 Test Your Credentials

You can test if your credentials work using AWS CLI:

```bash
aws sts get-caller-identity --region us-east-1
```

If this works, your credentials are valid. If not, you need to:
1. Generate new credentials in AWS Console
2. Update your `.env` file

## 📝 Steps to Fix

1. **Open your `.env` file:**
   ```bash
   nano .env
   # or
   code .env
   ```

2. **Remove any quotes** from around your credentials:
   ```bash
   # Change this:
   AWS_ACCESS_KEY_ID="AKIA..."
   
   # To this:
   AWS_ACCESS_KEY_ID=AKIA...
   ```

3. **Remove trailing spaces** - Make sure there are no spaces after the values

4. **Verify the format:**
   ```bash
   cat .env
   ```

5. **Restart your application:**
   - If using Streamlit: Stop and restart `streamlit run app.py`
   - If using CLI: Just run again

## 🔐 Getting New AWS Credentials

If your credentials are expired:

1. Go to [AWS IAM Console](https://console.aws.amazon.com/iam/)
2. Click "Users" → Select your user → "Security credentials"
3. Click "Create access key"
4. Choose "Command Line Interface (CLI)"
5. Copy the **Access Key ID** and **Secret Access Key**
6. Update your `.env` file (without quotes!)

## ⚠️ Security Note

- Never commit `.env` to git (it's in `.gitignore`)
- Don't share your credentials
- Use IAM roles when deploying to AWS (instead of access keys)

## 🆘 Still Having Issues?

1. Check the Debug Info section in the Streamlit UI sidebar
2. Verify Bedrock is enabled in your AWS account
3. Ensure your AWS user has permissions for Bedrock
4. Try using AWS CLI default credentials: `aws configure`

