"""Test specific query routing issue"""
from dotenv import load_dotenv
load_dotenv()

from app.graph.orchestrator import get_orchestrator
from app.graph.state import create_initial_state

# Test the specific query
query = "basic plan cost"

print("="*60)
print(f"Testing Query: '{query}'")
print("="*60)

# Create state with no previous messages
state = create_initial_state(query=query, session_id="test")
orchestrator = get_orchestrator()

# Route the query
state = orchestrator.route_query(state)

print(f"\nRouted to: {state['selected_agent']}")
print(f"Routing history: {state['routing_history']}")

# Also test some variations
test_queries = [
    "basic plan cost",
    "What is the basic plan cost?",
    "How much does the basic plan cost?",
    "cost of basic plan",
    "pricing for basic plan"
]

print("\n" + "="*60)
print("Testing query variations:")
print("="*60)

for q in test_queries:
    state = create_initial_state(query=q, session_id="test")
    state = orchestrator.route_query(state)
    agent = state['selected_agent']
    symbol = "[OK]" if agent == "billing" else "[WRONG]"
    print(f"{symbol} '{q}' -> {agent}")

