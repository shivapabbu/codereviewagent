#!/usr/bin/env python3
"""
Diagnostic script to test AWS credentials and Bedrock access
"""
import os
import json
import boto3
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)
load_dotenv(override=False)

def sanitize_credential(value):
    """Remove quotes and whitespace from credentials."""
    if not value:
        return None
    return value.strip().strip('"').strip("'").strip()

print("=" * 60)
print("AWS Credentials Diagnostic Tool")
print("=" * 60)
print()

# Check environment variables
aws_region = sanitize_credential(os.getenv("AWS_REGION")) or sanitize_credential(os.getenv("AWS_DEFAULT_REGION")) or "us-east-1"
aws_key_raw = os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("AWS_ACCESS_KEY")
aws_secret_raw = os.getenv("AWS_SECRET_ACCESS_KEY") or os.getenv("AWS_SECRET_KEY")

aws_key = sanitize_credential(aws_key_raw)
aws_secret = sanitize_credential(aws_secret_raw)

print(f"📁 .env file path: {env_path}")
print(f"✅ .env file exists: {env_path.exists()}")
print()

print("🔑 Credentials Check:")
print(f"   AWS_REGION: {aws_region}")
print(f"   AWS_ACCESS_KEY_ID: {'✅ Set' if aws_key else '❌ Not set'}")
if aws_key:
    print(f"      Length: {len(aws_key)} characters")
    print(f"      Preview: {aws_key[:10]}...{aws_key[-4:] if len(aws_key) > 14 else ''}")
    # Check for common issues
    if aws_key.startswith('"') or aws_key.startswith("'"):
        print(f"      ⚠️  WARNING: Key starts with quotes!")
    if aws_key.endswith('"') or aws_key.endswith("'"):
        print(f"      ⚠️  WARNING: Key ends with quotes!")
    if ' ' in aws_key:
        print(f"      ⚠️  WARNING: Key contains spaces!")
    if not aws_key.startswith('AKIA') and len(aws_key) == 20:
        print(f"      ⚠️  WARNING: Key doesn't start with 'AKIA' (unusual format)")
else:
    print(f"      Raw value: {aws_key_raw}")

print(f"   AWS_SECRET_ACCESS_KEY: {'✅ Set' if aws_secret else '❌ Not set'}")
if aws_secret:
    print(f"      Length: {len(aws_secret)} characters")
    print(f"      Preview: {aws_secret[:4]}...{aws_secret[-4:] if len(aws_secret) > 8 else ''}")
    # Check for common issues
    if aws_secret.startswith('"') or aws_secret.startswith("'"):
        print(f"      ⚠️  WARNING: Secret starts with quotes!")
    if aws_secret.endswith('"') or aws_secret.endswith("'"):
        print(f"      ⚠️  WARNING: Secret ends with quotes!")
    if ' ' in aws_secret:
        print(f"      ⚠️  WARNING: Secret contains spaces!")
else:
    print(f"      Raw value: {aws_secret_raw}")

# Check for session token
aws_session_token_raw = os.getenv("AWS_SESSION_TOKEN") or os.getenv("AWS_SECURITY_TOKEN")
aws_session_token = sanitize_credential(aws_session_token_raw)

is_temporary = aws_key and aws_key.startswith("ASIA")
print(f"   AWS_SESSION_TOKEN: {'✅ Set' if aws_session_token else '❌ Not set'}")
if is_temporary:
    if aws_session_token:
        print(f"      Length: {len(aws_session_token)} characters")
        print(f"      Preview: {aws_session_token[:20]}...{aws_session_token[-10:] if len(aws_session_token) > 30 else ''}")
    else:
        print(f"      🔴 CRITICAL: Temporary credentials (ASIA) require AWS_SESSION_TOKEN!")
        print(f"      Add AWS_SESSION_TOKEN=... to your .env file")
elif aws_session_token:
    print(f"      ℹ️  Session token present but not needed for permanent credentials")

print()

# Test AWS STS (Identity validation)
print("🧪 Testing AWS Credentials:")
try:
    if aws_key and aws_secret:
        client_params = {
            'service_name': 'sts',
            'region_name': aws_region,
            'aws_access_key_id': aws_key,
            'aws_secret_access_key': aws_secret
        }
        if aws_session_token:
            client_params['aws_session_token'] = aws_session_token
        elif is_temporary:
            print("   ❌ ERROR: Cannot test - temporary credentials require AWS_SESSION_TOKEN")
            print()
            print("   📋 Fix your .env file:")
            print("      Add this line:")
            print("      AWS_SESSION_TOKEN=your_session_token_here")
            print()
            exit(1)
        sts_client = boto3.client(**client_params)
    else:
        print("   ⚠️  Using default AWS credential chain...")
        sts_client = boto3.client('sts', region_name=aws_region)
    
    identity = sts_client.get_caller_identity()
    print(f"   ✅ Credentials are VALID!")
    print(f"   Account ID: {identity.get('Account', 'N/A')}")
    print(f"   User ARN: {identity.get('Arn', 'N/A')}")
    print(f"   User ID: {identity.get('UserId', 'N/A')}")
except Exception as e:
    print(f"   ❌ Credentials are INVALID: {e}")
    print()
    print("   💡 This means your credentials are wrong or expired.")
    print("   💡 Get new credentials from: https://console.aws.amazon.com/iam/")
    print()
    exit(1)

print()

# Test Bedrock access
print("🧪 Testing Bedrock Access:")
try:
    if aws_key and aws_secret:
        bedrock = boto3.client(
            'bedrock-runtime',
            region_name=aws_region,
            aws_access_key_id=aws_key,
            aws_secret_access_key=aws_secret
        )
    else:
        bedrock = boto3.client('bedrock-runtime', region_name=aws_region)
    
    # Just check if we can list models (this requires bedrock:ListFoundationModels permission)
    # Instead, we'll try to invoke a simple model call
    model_id = os.getenv("MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
    print(f"   Testing with model: {model_id}")
    
    # Build bedrock client with credentials
    if aws_key and aws_secret:
        bedrock_params = {
            'service_name': 'bedrock-runtime',
            'region_name': aws_region,
            'aws_access_key_id': aws_key,
            'aws_secret_access_key': aws_secret
        }
        if aws_session_token:
            bedrock_params['aws_session_token'] = aws_session_token
        bedrock = boto3.client(**bedrock_params)
    
    # Test invoke with minimal payload
    test_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 10,
        "messages": [{"role": "user", "content": "Hi"}]
    }
    
    response = bedrock.invoke_model(
        modelId=model_id,
        body=json.dumps(test_body)
    )
    print(f"   ✅ Bedrock access is VALID!")
    print(f"   ✅ Model invocation successful!")
    
except Exception as e:
    error_msg = str(e)
    print(f"   ❌ Bedrock access failed: {error_msg}")
    print()
    
    if "UnrecognizedClientException" in error_msg or "invalid" in error_msg.lower():
        print("   💡 This error usually means:")
        print("      1. Credentials are invalid (already checked above)")
        print("      2. Credentials don't have Bedrock permissions")
        print("      3. Model access not enabled in AWS Console")
        print()
        print("   📋 Steps to fix:")
        print("      1. Go to: https://console.aws.amazon.com/bedrock/")
        print("      2. Click 'Model access' in left sidebar")
        print("      3. Request access to Claude 3 Sonnet")
        print("      4. Wait for approval (usually instant)")
    elif "AccessDeniedException" in error_msg:
        print("   💡 Your credentials don't have Bedrock permissions.")
        print("   💡 Add 'bedrock:InvokeModel' permission to your IAM user.")
    elif "ValidationException" in error_msg:
        print("   💡 Model ID might be incorrect or not available in this region.")
        print(f"   💡 Check available models in region: {aws_region}")
    else:
        print(f"   💡 Unexpected error type: {type(e).__name__}")

print()
print("=" * 60)

