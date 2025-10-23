"""Quick test to debug Bedrock routing"""
import os
from dotenv import load_dotenv
load_dotenv()

from app.llm_providers import get_orchestrator_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Create the routing LLM (Bedrock)
routing_llm = get_orchestrator_llm()

# Create the routing prompt
routing_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a routing specialist for a customer service system. 
Your job is to analyze customer queries and determine which specialized agent should handle them.

Available agents:
1. BILLING - Handles questions about pricing, plans, invoices, payments, subscriptions, upgrades/downgrades
2. TECHNICAL - Handles technical support, troubleshooting, account setup, API issues, authentication, webhooks
3. POLICY - Handles questions about terms of service, privacy policy, GDPR, data retention, compliance, legal matters

IMPORTANT: Route based ONLY on the current query below. Ignore any previous conversation context.
Each query should be routed independently based on its topic.

Analyze the query and respond with ONLY the agent name (billing, technical, or policy) in lowercase.
If the query is ambiguous, choose the most likely agent based on keywords in the current query."""),
    ("human", "Current Query: {query}\n\nWhich agent should handle this specific query? Respond with only: billing, technical, or policy")
])

# Test queries
test_queries = [
    "What are your pricing plans?",
    "How do I reset my password?",
    "What is your privacy policy?"
]

print("="*60)
print("TESTING BEDROCK ROUTING")
print("="*60)
print(f"Model: {routing_llm.model_id}")
print(f"Type: {type(routing_llm)}")
print()

for query in test_queries:
    print(f"\nQuery: {query}")
    try:
        # Test the chain
        chain = routing_prompt | routing_llm | StrOutputParser()
        result = chain.invoke({"query": query})
        print(f"[OK] Response: '{result}'")
        print(f"     Stripped/Lower: '{result.strip().lower()}'")
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

print("\n" + "="*60)

