#!/usr/bin/env python3
"""
Test script for the LangGraph orchestrator.

Tests intelligent routing to different specialized agents based on query content.

Usage:
    python test_orchestrator.py
"""

import sys
import asyncio
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.graph.orchestrator import process_query, process_query_with_streaming
from app.graph.state import create_initial_state


# Test queries for different agents
TEST_QUERIES = {
    "billing": [
        "What are your pricing plans?",
        "How much does the Enterprise plan cost?",
        "Can I see my invoice from last month?",
        "What payment methods do you accept?",
        "How do I upgrade my subscription?"
    ],
    "technical": [
        "How do I reset my password?",
        "My API authentication is failing, what should I do?",
        "How do I set up webhooks?",
        "I'm getting a 401 error, can you help?",
        "How do I integrate with your API?"
    ],
    "policy": [
        "What is your privacy policy?",
        "Are you GDPR compliant?",
        "What is your data retention policy?",
        "What are your terms of service?",
        "How do you handle user data?"
    ]
}


def test_routing_accuracy():
    """Test that queries are routed to the correct agents."""
    print("\n" + "=" * 70)
    print("TESTING ROUTING ACCURACY")
    print("=" * 70)
    
    correct_routes = 0
    total_queries = 0
    
    for expected_agent, queries in TEST_QUERIES.items():
        print(f"\n{expected_agent.upper()} Queries:")
        print("-" * 70)
        
        for query in queries:
            total_queries += 1
            
            # Process query
            result = process_query(
                query=query,
                session_id=f"test_{expected_agent}_{total_queries}"
            )
            
            # Check routing
            actual_agent = result.get("agent", "Unknown")
            routed_correctly = expected_agent.lower() in actual_agent.lower()
            
            if routed_correctly:
                correct_routes += 1
                status = "[OK]"
            else:
                status = "[X]"
            
            print(f"{status} Query: \"{query}\"")
            print(f"  -> Routed to: {actual_agent}")
            print(f"  -> Strategy: {result.get('strategy')}")
            print()
    
    # Calculate accuracy
    accuracy = (correct_routes / total_queries) * 100 if total_queries > 0 else 0
    
    print("=" * 70)
    print(f"Routing Accuracy: {correct_routes}/{total_queries} ({accuracy:.1f}%)")
    print("=" * 70)
    
    return accuracy >= 80  # At least 80% accuracy


def test_full_workflow():
    """Test complete workflow with sample queries."""
    print("\n" + "=" * 70)
    print("TESTING FULL WORKFLOW")
    print("=" * 70)
    
    test_cases = [
        {
            "query": "What's included in the Professional plan?",
            "expected_agent": "billing"
        },
        {
            "query": "How do I enable two-factor authentication?",
            "expected_agent": "technical"
        },
        {
            "query": "What rights do I have under GDPR?",
            "expected_agent": "policy"
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        query = test_case["query"]
        expected = test_case["expected_agent"]
        
        print(f"\nTest Case {i}:")
        print(f"Query: \"{query}\"")
        print(f"Expected Agent: {expected}")
        
        # Process query
        result = process_query(
            query=query,
            session_id=f"workflow_test_{i}"
        )
        
        # Display results
        actual_agent = result.get("agent", "Unknown")
        response = result.get("response", "No response")
        processing_time = result.get("processing_time", 0)
        
        print(f"Actual Agent: {actual_agent}")
        print(f"Processing Time: {processing_time:.2f}s")
        print(f"Response Preview: {response[:150]}...")
        
        # Check if routed correctly
        passed = expected.lower() in actual_agent.lower()
        print(f"Result: {'[PASS]' if passed else '[FAIL]'}")
        
        if not passed:
            all_passed = False
        
        # Show routing history
        routing_history = result.get("routing_history", [])
        if routing_history:
            print(f"Routing Decision: {routing_history[0]}")
    
    return all_passed


async def test_streaming():
    """Test streaming responses from orchestrator."""
    print("\n" + "=" * 70)
    print("TESTING STREAMING RESPONSES")
    print("=" * 70)
    
    query = "What are the main features of your pricing plans?"
    session_id = "streaming_test"
    
    print(f"\nQuery: \"{query}\"")
    print("\nStreaming Response:")
    print("-" * 70)
    
    try:
        async for chunk in process_query_with_streaming(query, session_id):
            print(chunk, end="", flush=True)
        
        print("\n" + "-" * 70)
        print("[SUCCESS] Streaming completed successfully")
        return True
        
    except Exception as e:
        print(f"\n[FAILED] Streaming failed: {e}")
        return False


def test_conversation_context():
    """Test that orchestrator maintains conversation context."""
    print("\n" + "=" * 70)
    print("TESTING CONVERSATION CONTEXT")
    print("=" * 70)
    
    session_id = "context_test"
    
    # First query
    print("\nQuery 1: Initial pricing question")
    result1 = process_query(
        query="What are your pricing plans?",
        session_id=session_id
    )
    print(f"Agent: {result1.get('agent')}")
    print(f"Response: {result1.get('response', '')[:150]}...")
    
    # Follow-up query (should maintain context)
    print("\nQuery 2: Follow-up question")
    result2 = process_query(
        query="What about the features included?",
        session_id=session_id,
        messages=result1.get("messages", [])
    )
    print(f"Agent: {result2.get('agent')}")
    print(f"Response: {result2.get('response', '')[:150]}...")
    
    return result1.get("success") and result2.get("success")


def main():
    """Run all orchestrator tests."""
    print("\n" + "=" * 70)
    print("LANGGRAPH ORCHESTRATOR TESTING SUITE")
    print("=" * 70)
    
    try:
        # Run tests
        routing_passed = test_routing_accuracy()
        workflow_passed = test_full_workflow()
        streaming_passed = asyncio.run(test_streaming())
        context_passed = test_conversation_context()
        
        # Summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        
        tests = [
            ("Routing Accuracy", routing_passed),
            ("Full Workflow", workflow_passed),
            ("Streaming", streaming_passed),
            ("Conversation Context", context_passed)
        ]
        
        for name, passed in tests:
            status = "[PASS]" if passed else "[FAIL]"
            print(f"{status} - {name}")
        
        all_passed = all(passed for _, passed in tests)
        
        print("\n" + "=" * 70)
        if all_passed:
            print("[SUCCESS] ALL TESTS PASSED")
            print("\nThe orchestrator is working correctly:")
            print("  - Routes queries to appropriate agents")
            print("  - Handles streaming responses")
            print("  - Maintains conversation context")
            print("  - Uses Bedrock Claude for cost-effective routing")
        else:
            print("[FAILED] SOME TESTS FAILED")
            print("\nPlease check:")
            print("  1. All agents are properly initialized")
            print("  2. LLM providers are configured")
            print("  3. ChromaDB collections exist")
        
        print("=" * 70 + "\n")
        
        return 0 if all_passed else 1
    
    except Exception as e:
        print(f"\n[ERROR] Error running tests: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

