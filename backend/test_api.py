#!/usr/bin/env python3
"""
Test script for FastAPI endpoints.

Tests the chat API with streaming and non-streaming modes.

Usage:
    # Start the server first:
    python -m app.main
    
    # Then run this script:
    python test_api.py
"""

import sys
import requests
import json
import time
from typing import Dict


# API base URL
API_URL = "http://localhost:8000"


def test_health_check():
    """Test the health check endpoint."""
    print("\n" + "=" * 70)
    print("TESTING HEALTH CHECK")
    print("=" * 70)
    
    try:
        response = requests.get(f"{API_URL}/health")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Status: {data['status']}")
            print(f"  OpenAI Configured: {data['openai_configured']}")
            print(f"  AWS Configured: {data['aws_configured']}")
            print(f"  LLM Providers: {data.get('llm_providers', {})}")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to API server")
        print("  Please start the server with: python -m app.main")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_non_streaming_chat():
    """Test non-streaming chat endpoint."""
    print("\n" + "=" * 70)
    print("TESTING NON-STREAMING CHAT")
    print("=" * 70)
    
    test_queries = [
        "What are your pricing plans?",
        "How do I reset my password?",
        "What is your privacy policy?"
    ]
    
    try:
        for query in test_queries:
            print(f"\nQuery: \"{query}\"")
            
            response = requests.post(
                f"{API_URL}/api/chat",
                json={
                    "message": query,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Agent: {data['agent']}")
                print(f"  Strategy: {data['strategy']}")
                print(f"  Processing Time: {data['processing_time']:.2f}s")
                print(f"  Response: {data['response'][:150]}...")
            else:
                print(f"✗ Request failed: {response.status_code}")
                print(f"  {response.text}")
                return False
        
        return True
    
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_streaming_chat():
    """Test streaming chat endpoint."""
    print("\n" + "=" * 70)
    print("TESTING STREAMING CHAT")
    print("=" * 70)
    
    query = "What features are included in the Professional plan?"
    print(f"\nQuery: \"{query}\"")
    print("\nStreaming Response:")
    print("-" * 70)
    
    try:
        response = requests.post(
            f"{API_URL}/api/chat",
            json={
                "message": query,
                "stream": True
            },
            stream=True,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"✗ Request failed: {response.status_code}")
            return False
        
        # Parse SSE stream
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                
                if line.startswith('data: '):
                    data_str = line[6:]  # Remove 'data: ' prefix
                    
                    try:
                        data = json.loads(data_str)
                        
                        if data['type'] == 'chunk':
                            print(data['content'], end='', flush=True)
                        elif data['type'] == 'done':
                            print("\n" + "-" * 70)
                            print("✓ Streaming completed successfully")
                        elif data['type'] == 'error':
                            print(f"\n✗ Stream error: {data['error']}")
                            return False
                    
                    except json.JSONDecodeError:
                        pass
        
        return True
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def test_session_management():
    """Test session management endpoints."""
    print("\n" + "=" * 70)
    print("TESTING SESSION MANAGEMENT")
    print("=" * 70)
    
    try:
        # Create a session with multiple messages
        session_id = f"test_session_{int(time.time())}"
        
        print(f"\n1. Creating session: {session_id}")
        
        # Send first message
        response1 = requests.post(
            f"{API_URL}/api/chat",
            json={
                "message": "What are your pricing plans?",
                "session_id": session_id,
                "stream": False
            }
        )
        
        if response1.status_code != 200:
            print(f"✗ First message failed: {response1.status_code}")
            return False
        
        print("✓ First message sent")
        
        # Send second message in same session
        response2 = requests.post(
            f"{API_URL}/api/chat",
            json={
                "message": "What about the Enterprise plan?",
                "session_id": session_id,
                "stream": False
            }
        )
        
        if response2.status_code != 200:
            print(f"✗ Second message failed: {response2.status_code}")
            return False
        
        print("✓ Second message sent")
        
        # Get session info
        print(f"\n2. Retrieving session information")
        session_response = requests.get(f"{API_URL}/api/chat/sessions/{session_id}")
        
        if session_response.status_code == 200:
            session_data = session_response.json()
            print(f"✓ Session retrieved")
            print(f"  Message count: {session_data['message_count']}")
            print(f"  Created at: {session_data['created_at']}")
        else:
            print(f"✗ Failed to retrieve session")
            return False
        
        # List all sessions
        print(f"\n3. Listing all sessions")
        list_response = requests.get(f"{API_URL}/api/chat/sessions")
        
        if list_response.status_code == 200:
            sessions = list_response.json()
            print(f"✓ Active sessions: {sessions['count']}")
        else:
            print(f"✗ Failed to list sessions")
            return False
        
        # Delete session
        print(f"\n4. Deleting session")
        delete_response = requests.delete(f"{API_URL}/api/chat/sessions/{session_id}")
        
        if delete_response.status_code == 200:
            print(f"✓ Session deleted")
        else:
            print(f"✗ Failed to delete session")
            return False
        
        return True
    
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_routing_endpoint():
    """Test the routing test endpoint."""
    print("\n" + "=" * 70)
    print("TESTING ROUTING TEST ENDPOINT")
    print("=" * 70)
    
    test_queries = [
        ("What's the Enterprise plan pricing?", "billing"),
        ("How do I set up webhooks?", "technical"),
        ("What's your GDPR policy?", "policy")
    ]
    
    try:
        for query, expected_agent in test_queries:
            print(f"\nQuery: \"{query}\"")
            print(f"Expected Agent: {expected_agent}")
            
            response = requests.post(
                f"{API_URL}/api/chat/test",
                json={"message": query}
            )
            
            if response.status_code == 200:
                data = response.json()
                actual_agent = data['selected_agent']
                
                if actual_agent == expected_agent:
                    print(f"✓ Correctly routed to: {actual_agent}")
                else:
                    print(f"⚠ Routed to: {actual_agent} (expected: {expected_agent})")
            else:
                print(f"✗ Request failed: {response.status_code}")
                return False
        
        return True
    
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Run all API tests."""
    print("\n" + "=" * 70)
    print("FASTAPI ENDPOINT TESTING SUITE")
    print("=" * 70)
    print(f"\nAPI URL: {API_URL}")
    
    # Run tests
    tests = [
        ("Health Check", test_health_check),
        ("Non-Streaming Chat", test_non_streaming_chat),
        ("Streaming Chat", test_streaming_chat),
        ("Session Management", test_session_management),
        ("Routing Test Endpoint", test_routing_endpoint)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n✗ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(passed for _, passed in results)
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✓ ALL TESTS PASSED")
        print("\nThe API is working correctly:")
        print("  - Health check functional")
        print("  - Non-streaming responses working")
        print("  - Streaming responses working")
        print("  - Session management working")
        print("  - Routing test endpoint working")
    else:
        print("✗ SOME TESTS FAILED")
        print("\nPlease check:")
        print("  1. Server is running (python -m app.main)")
        print("  2. All dependencies are installed")
        print("  3. LLM providers are configured")
        print("  4. ChromaDB collections exist")
    
    print("=" * 70 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

