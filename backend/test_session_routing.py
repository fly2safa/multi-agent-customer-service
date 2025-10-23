"""Test routing with session context like in real usage"""
from dotenv import load_dotenv
load_dotenv()

from app.graph.orchestrator import get_orchestrator
from app.graph.state import create_initial_state
from langchain_core.messages import HumanMessage, AIMessage

# Simulate a conversation where Technical Support was used first
print("="*60)
print("Simulating Real Conversation Flow")
print("="*60)

orchestrator = get_orchestrator()
session_id = "test_session_123"

# First query - Technical Support
query1 = "How do I reset my password?"
messages1 = []

state1 = create_initial_state(query=query1, session_id=session_id, messages=messages1)
state1 = orchestrator.route_query(state1)

print(f"\n1. Query: '{query1}'")
print(f"   Routed to: {state1['selected_agent']}")

# Add to message history
messages2 = [
    {"role": "human", "content": query1},
    {"role": "ai", "content": "To reset your password..."}
]

# Second query - Should route to Billing
query2 = "basic plan cost"

state2 = create_initial_state(query=query2, session_id=session_id, messages=messages2)
state2 = orchestrator.route_query(state2)

print(f"\n2. Query: '{query2}'")
print(f"   Previous context: Technical Support was last agent")
print(f"   Routed to: {state2['selected_agent']}")
print(f"   Expected: billing")
print(f"   Result: {'[OK]' if state2['selected_agent'] == 'billing' else '[WRONG]'}")

# Check routing decision details
print(f"\n   Routing decision details:")
print(f"   {state2['routing_history'][-1]}")

print("\n" + "="*60)

