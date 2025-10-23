#!/usr/bin/env python3
"""
Diagnostic script to test AWS Bedrock connectivity
"""

import boto3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_aws_credentials():
    """Test if AWS credentials are valid"""
    print("=" * 70)
    print("TESTING AWS CREDENTIALS")
    print("=" * 70)
    
    try:
        # Test STS (Security Token Service) to verify credentials
        sts_client = boto3.client(
            'sts',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            aws_session_token=os.getenv('AWS_SESSION_TOKEN')
        )
        
        identity = sts_client.get_caller_identity()
        print(f"[OK] AWS Credentials Valid!")
        print(f"     Account: {identity['Account']}")
        print(f"     User ARN: {identity['Arn']}")
        print(f"     Region: {os.getenv('AWS_REGION')}")
        return True
        
    except Exception as e:
        print(f"[ERROR] AWS Credentials Invalid: {e}")
        return False


def test_bedrock_access():
    """Test if Bedrock service is accessible"""
    print("\n" + "=" * 70)
    print("TESTING BEDROCK SERVICE ACCESS")
    print("=" * 70)
    
    try:
        # Create Bedrock client
        bedrock_client = boto3.client(
            'bedrock',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            aws_session_token=os.getenv('AWS_SESSION_TOKEN')
        )
        
        # List available foundation models
        print("[INFO] Attempting to list Bedrock models...")
        response = bedrock_client.list_foundation_models()
        
        print(f"[OK] Bedrock Service Accessible!")
        print(f"     Total models available: {len(response['modelSummaries'])}")
        
        # Check if Claude models are available
        claude_models = [m for m in response['modelSummaries'] if 'claude' in m['modelId'].lower()]
        print(f"     Claude models available: {len(claude_models)}")
        
        if claude_models:
            print("\n     Available Claude Models:")
            for model in claude_models:
                print(f"     - {model['modelId']}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Bedrock Service Not Accessible: {e}")
        print("\n[INFO] Common Causes:")
        print("  1. Bedrock not available in this region")
        print("  2. Bedrock not enabled for your AWS account")
        print("  3. IAM permissions missing for Bedrock")
        print("  4. AWS Academy account limitations")
        return False


def test_bedrock_runtime():
    """Test if Bedrock Runtime (for inference) is accessible"""
    print("\n" + "=" * 70)
    print("TESTING BEDROCK RUNTIME (INFERENCE)")
    print("=" * 70)
    
    try:
        # Create Bedrock Runtime client
        bedrock_runtime = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            aws_session_token=os.getenv('AWS_SESSION_TOKEN')
        )
        
        # Try to invoke a simple model (Claude 3.5 Haiku)
        model_id = os.getenv('BEDROCK_MODEL', 'anthropic.claude-3-5-haiku-20241022-v1:0')
        print(f"[INFO] Testing model: {model_id}")
        
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body='{"anthropic_version":"bedrock-2023-05-31","max_tokens":50,"messages":[{"role":"user","content":"Hello"}]}'
        )
        
        print(f"[OK] Bedrock Runtime Works!")
        print(f"     Successfully invoked: {model_id}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Bedrock Runtime Failed: {e}")
        print(f"\n[INFO] Error Type: {type(e).__name__}")
        
        if "UnrecognizedClientException" in str(e):
            print("\n[DIAGNOSIS] UnrecognizedClientException means:")
            print("  - Session token might be expired (AWS Academy tokens expire quickly)")
            print("  - Wrong credentials for this region")
            print("  - Credentials not refreshed after lab restart")
            print("\n[ACTION] Try:")
            print("  1. Check if your AWS Academy Lab is still running")
            print("  2. Get fresh credentials from AWS Academy -> AWS Details -> Show")
            print("  3. Update ALL three values in .env (access key, secret, session token)")
            
        elif "ValidationException" in str(e):
            print("\n[DIAGNOSIS] Model not available in this region")
            print("  Try changing AWS_REGION in .env to: us-west-2")
            
        return False


def main():
    print("\n")
    print("=" * 70)
    print("AWS BEDROCK DIAGNOSTIC TOOL")
    print("=" * 70)
    print()
    
    # Step 1: Test AWS credentials
    creds_valid = test_aws_credentials()
    
    if not creds_valid:
        print("\n[STOP] Fix AWS credentials first before testing Bedrock")
        return
    
    # Step 2: Test Bedrock service access
    bedrock_accessible = test_bedrock_access()
    
    # Step 3: Test Bedrock Runtime (inference)
    runtime_works = test_bedrock_runtime()
    
    # Summary
    print("\n" + "=" * 70)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 70)
    print(f"AWS Credentials: {'[OK]' if creds_valid else '[FAILED]'}")
    print(f"Bedrock Service: {'[OK]' if bedrock_accessible else '[FAILED]'}")
    print(f"Bedrock Runtime: {'[OK]' if runtime_works else '[FAILED]'}")
    print("=" * 70)
    print()
    
    if runtime_works:
        print("[SUCCESS] Bedrock is fully configured! You can proceed with testing.")
    else:
        print("[ACTION NEEDED] Follow the error messages above to fix Bedrock access.")


if __name__ == "__main__":
    main()


