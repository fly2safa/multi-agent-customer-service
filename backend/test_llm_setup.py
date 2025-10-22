#!/usr/bin/env python3
"""
Test script to validate LLM provider configuration.

Run this script to verify that OpenAI and AWS Bedrock are properly configured
before running the main application.

Usage:
    python test_llm_setup.py
"""

import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings
from app.llm_providers import validate_llm_configuration, get_openai_llm, get_bedrock_llm
from app.retrievers import get_retriever_manager


def test_configuration():
    """Test configuration and credentials."""
    print("\n" + "=" * 70)
    print("TESTING LLM PROVIDER CONFIGURATION")
    print("=" * 70)
    
    # Check environment variables
    print("\n1. Environment Variables:")
    print(f"   OPENAI_API_KEY: {'[OK] Set' if settings.OPENAI_API_KEY else '[X] Not set'}")
    print(f"   AWS_ACCESS_KEY_ID: {'[OK] Set' if settings.AWS_ACCESS_KEY_ID else '[X] Not set'}")
    print(f"   AWS_SECRET_ACCESS_KEY: {'[OK] Set' if settings.AWS_SECRET_ACCESS_KEY else '[X] Not set'}")
    print(f"   AWS_REGION: {settings.AWS_REGION}")
    
    # Validate LLM providers
    print("\n2. LLM Provider Validation:")
    results = validate_llm_configuration()
    
    for provider, status in results.items():
        print(f"\n   {provider.upper()}:")
        if status["configured"]:
            print(f"      [OK] Configured successfully")
        else:
            print(f"      [X] Configuration failed")
            if status["error"]:
                print(f"      Error: {status['error']}")
    
    # Test ChromaDB collections
    print("\n3. ChromaDB Collections:")
    try:
        manager = get_retriever_manager()
        collections = manager.list_collections()
        
        if collections:
            print(f"   [OK] Found {len(collections)} collections:")
            for collection_name in collections:
                stats = manager.get_collection_stats(collection_name)
                if "error" not in stats:
                    print(f"      - {collection_name}: {stats['count']} documents")
                else:
                    print(f"      - {collection_name}: Error - {stats['error']}")
        else:
            print("   [X] No collections found")
            print("   Run 'python ingest_data.py' to create collections")
    
    except Exception as e:
        print(f"   [X] Error accessing ChromaDB: {e}")
        print("   Run 'python ingest_data.py' to initialize database")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    all_configured = all(r["configured"] for r in results.values())
    
    if all_configured:
        print("[OK] All LLM providers are configured correctly!")
        print("\nYou can now:")
        print("  1. Run the data ingestion: python ingest_data.py")
        print("  2. Start the API server: python -m app.main")
    else:
        print("[X] Some LLM providers are not configured properly")
        print("\nPlease check:")
        print("  1. Your .env file has the correct API keys")
        print("  2. OpenAI API key is valid")
        print("  3. AWS credentials have Bedrock access")
        print("  4. AWS region supports Bedrock (us-east-1 recommended)")
    
    print("\n" + "=" * 70 + "\n")
    
    return all_configured


def test_simple_query():
    """Test a simple query to each LLM provider."""
    print("\n" + "=" * 70)
    print("TESTING SIMPLE QUERIES (Optional)")
    print("=" * 70)
    
    test_query = input("\nWould you like to test with a simple query? (y/n): ").lower().strip()
    
    if test_query != 'y':
        print("Skipping query test.")
        return
    
    # Test OpenAI
    print("\n1. Testing OpenAI (GPT-4)...")
    try:
        llm = get_openai_llm(streaming=False, temperature=0.7, max_tokens=100)
        response = llm.invoke("Say 'OpenAI connection successful' in a friendly way.")
        print(f"   [OK] OpenAI Response: {response.content}")
    except Exception as e:
        print(f"   [X] OpenAI Error: {e}")
    
    # Test Bedrock
    print("\n2. Testing AWS Bedrock (Claude 3.5 Haiku)...")
    try:
        llm = get_bedrock_llm(temperature=0.3, max_tokens=100)
        response = llm.invoke("Say 'Bedrock connection successful' in a friendly way.")
        print(f"   [OK] Bedrock Response: {response.content}")
    except Exception as e:
        print(f"   [X] Bedrock Error: {e}")
    
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    try:
        success = test_configuration()
        
        if success:
            test_simple_query()
        
        sys.exit(0 if success else 1)
    
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

