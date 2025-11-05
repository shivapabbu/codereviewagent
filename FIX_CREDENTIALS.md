# 🔧 Quick Fix: Invalid Credentials Error

## ✅ Your Issue: Credentials are Expired

The diagnostic shows:
- ✅ `AWS_SESSION_TOKEN` is set (good!)
- ❌ But credentials are **expired or invalid**

Temporary credentials (ASIA prefix) expire after a few hours. You need fresh ones.

## 🚀 Quick Solutions

### Option 1: Refresh Using AWS CLI (Easiest)

```bash
# Run the helper script
./refresh_credentials.sh

# Or manually:
aws sso login  # If using SSO
aws configure export-credentials --format env
```

Copy the output and update your `.env` file.

### Option 2: Get Permanent Credentials (Recommended)

Permanent credentials don't expire and are easier to manage:

1. Go to [AWS IAM Console](https://console.aws.amazon.com/iam/)
2. Click **Users** → Select your user → **Security credentials** tab
3. Scroll to **Access keys** → Click **Create access key**
4. Choose **Command Line Interface (CLI)**
5. Copy the **Access Key ID** (starts with `AKIA`)
6. Copy the **Secret Access Key**
7. Update your `.env`:

```bash
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...  # New permanent key
AWS_SECRET_ACCESS_KEY=...  # New secret
# Remove AWS_SESSION_TOKEN line (not needed for permanent keys)
MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

### Option 3: Use AWS CLI Default Credentials

If you have AWS CLI configured:

```bash
aws configure
```

Then remove credentials from `.env` and let the app use the default credential chain.

## 🧪 Test After Fixing

```bash
python3 test_credentials.py
```

Should show:
- ✅ Credentials are VALID
- ✅ Bedrock access is VALID

## ⚠️ Important Notes

1. **Temporary credentials expire** - They last 1-12 hours typically
2. **Permanent credentials are better for development** - They don't expire
3. **Never commit `.env`** - It contains sensitive credentials
4. **Rotate credentials regularly** - For security

## 📋 Still Having Issues?

1. Check if Bedrock is enabled: https://console.aws.amazon.com/bedrock/
2. Verify your IAM user has Bedrock permissions
3. Check the region is correct (us-east-1, us-west-2, etc.)
4. Run `python3 test_credentials.py` for detailed diagnostics

