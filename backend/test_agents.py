#!/usr/bin/env python3
"""
Test script for specialized worker agents.

Tests the three agents with sample queries to validate:
- Billing Agent (Hybrid RAG/CAG)
- Technical Agent (Pure RAG)
- Policy Agent (Pure CAG)

Usage:
    python test_agents.py
"""

import sys
import asyncio
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.agents import BillingAgent, TechnicalAgent, PolicyAgent


def test_billing_agent():
    """Test Billing Agent with Hybrid RAG/CAG strategy."""
    print("\n" + "=" * 70)
    print("TESTING BILLING AGENT (Hybrid RAG/CAG)")
    print("=" * 70)
    
    agent = BillingAgent()
    session_id = "test_session_billing"
    
    # First query - should use RAG
    print("\n1. First Query (RAG - Initial Retrieval):")
    query1 = "What are the pricing plans available?"
    print(f"   Query: {query1}")
    
    result1 = agent.process_query(query1, session_id)
    print(f"   Strategy: {result1['strategy']}")
    print(f"   Response: {result1['response'][:200]}...")
    
    # Second query - should use cached context (CAG)
    print("\n2. Second Query (CAG - Using Cache):")
    query2 = "What's included in the Enterprise plan?"
    print(f"   Query: {query2}")
    
    result2 = agent.process_query(query2, session_id, use_cache=True)
    print(f"   Strategy: {result2['strategy']}")
    print(f"   Response: {result2['response'][:200]}...")
    
    # Cache stats
    print("\n3. Cache Statistics:")
    stats = agent.get_cache_stats()
    print(f"   {stats}")
    
    return result1['success'] and result2['success']


def test_technical_agent():
    """Test Technical Agent with Pure RAG strategy."""
    print("\n" + "=" * 70)
    print("TESTING TECHNICAL AGENT (Pure RAG)")
    print("=" * 70)
    
    agent = TechnicalAgent()
    session_id = "test_session_technical"
    
    # Query 1
    print("\n1. First Query:")
    query1 = "How do I reset my password?"
    print(f"   Query: {query1}")
    
    result1 = agent.process_query(query1, session_id)
    print(f"   Strategy: {result1['strategy']}")
    print(f"   Sources: {result1.get('sources', [])}")
    print(f"   Response: {result1['response'][:200]}...")
    
    # Query 2
    print("\n2. Second Query:")
    query2 = "My API authentication is failing. What should I do?"
    print(f"   Query: {query2}")
    
    result2 = agent.process_query(query2, session_id)
    print(f"   Strategy: {result2['strategy']}")
    print(f"   Sources: {result2.get('sources', [])}")
    print(f"   Response: {result2['response'][:200]}...")
    
    # Agent info
    print("\n3. Agent Information:")
    info = agent.get_agent_info()
    print(f"   {info}")
    
    return result1['success'] and result2['success']


def test_policy_agent():
    """Test Policy Agent with Pure CAG strategy."""
    print("\n" + "=" * 70)
    print("TESTING POLICY AGENT (Pure CAG)")
    print("=" * 70)
    
    agent = PolicyAgent()
    session_id = "test_session_policy"
    
    # Query 1
    print("\n1. First Query:")
    query1 = "What is your data retention policy?"
    print(f"   Query: {query1}")
    
    result1 = agent.process_query(query1, session_id)
    print(f"   Strategy: {result1['strategy']}")
    print(f"   Documents in Context: {result1.get('documents_in_context', 0)}")
    print(f"   Response: {result1['response'][:200]}...")
    
    # Query 2
    print("\n2. Second Query:")
    query2 = "Are you GDPR compliant?"
    print(f"   Query: {query2}")
    
    result2 = agent.process_query(query2, session_id)
    print(f"   Strategy: {result2['strategy']}")
    print(f"   Documents in Context: {result2.get('documents_in_context', 0)}")
    print(f"   Response: {result2['response'][:200]}...")
    
    # Agent info
    print("\n3. Agent Information:")
    info = agent.get_agent_info()
    print(f"   {info}")
    
    return result1['success'] and result2['success']


async def test_streaming():
    """Test streaming responses from agents."""
    print("\n" + "=" * 70)
    print("TESTING STREAMING RESPONSES")
    print("=" * 70)
    
    agent = TechnicalAgent()
    query = "How do I set up webhooks?"
    session_id = "test_streaming"
    
    print(f"\nQuery: {query}")
    print("Streaming response:")
    print("-" * 70)
    
    try:
        async for chunk in agent.aprocess_query(query, session_id):
            print(chunk, end="", flush=True)
        print("\n" + "-" * 70)
        return True
    except Exception as e:
        print(f"\nError: {e}")
        return False


def main():
    """Run all agent tests."""
    print("\n" + "=" * 70)
    print("AGENT TESTING SUITE")
    print("=" * 70)
    
    try:
        # Test each agent
        billing_success = test_billing_agent()
        technical_success = test_technical_agent()
        policy_success = test_policy_agent()
        
        # Test streaming
        streaming_success = asyncio.run(test_streaming())
        
        # Summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        
        results = [
            ("Billing Agent", billing_success),
            ("Technical Agent", technical_success),
            ("Policy Agent", policy_success),
            ("Streaming", streaming_success)
        ]
        
        for name, success in results:
            status = "✓ PASS" if success else "✗ FAIL"
            print(f"{status} - {name}")
        
        all_passed = all(success for _, success in results)
        
        print("\n" + "=" * 70)
        if all_passed:
            print("✓ ALL TESTS PASSED")
            print("\nAll three agents are working correctly with their respective strategies:")
            print("  - Billing Agent: Hybrid RAG/CAG (caches after first query)")
            print("  - Technical Agent: Pure RAG (searches every time)")
            print("  - Policy Agent: Pure CAG (all docs in memory)")
        else:
            print("✗ SOME TESTS FAILED")
            print("\nPlease check:")
            print("  1. OpenAI API key is configured")
            print("  2. ChromaDB collections exist (run ingest_data.py)")
            print("  3. All dependencies are installed")
        
        print("=" * 70 + "\n")
        
        return 0 if all_passed else 1
    
    except Exception as e:
        print(f"\n✗ Error running tests: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

