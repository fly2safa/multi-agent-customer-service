"""
State Management for Multi-Agent System

Defines the state schema used throughout the LangGraph workflow,
including conversation history, routing decisions, and session data.
"""

from typing import TypedDict, List, Dict, Optional, Annotated
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from operator import add


class AgentState(TypedDict):
    """
    State for the multi-agent conversation workflow.
    
    This state is passed through all nodes in the LangGraph workflow
    and accumulates information about the conversation.
    """
    
    # Current user query
    query: str
    
    # Conversation history (list of messages)
    messages: Annotated[List, add]
    
    # Session identifier
    session_id: str
    
    # Selected agent for this query
    selected_agent: Optional[str]
    
    # Routing history (which agents have been called)
    routing_history: Annotated[List[Dict], add]
    
    # Agent response
    response: Optional[str]
    
    # Session-specific data (caches, context, etc.)
    session_data: Dict
    
    # Metadata about the interaction
    metadata: Dict
    
    # Error information if something goes wrong
    error: Optional[str]


def create_initial_state(
    query: str,
    session_id: str,
    messages: Optional[List] = None,
    session_data: Optional[Dict] = None
) -> AgentState:
    """
    Create an initial state for a new query.
    
    Args:
        query: User's question
        session_id: Unique session identifier
        messages: Previous conversation messages
        session_data: Session-specific cached data
        
    Returns:
        AgentState dictionary initialized for the query
    """
    return AgentState(
        query=query,
        messages=messages or [],
        session_id=session_id,
        selected_agent=None,
        routing_history=[],
        response=None,
        session_data=session_data or {},
        metadata={
            "timestamp": None,
            "processing_time": None,
            "tokens_used": None
        },
        error=None
    )


def add_message(state: AgentState, role: str, content: str) -> AgentState:
    """
    Add a message to the conversation history.
    
    Args:
        state: Current agent state
        role: Message role (human, ai, system)
        content: Message content
        
    Returns:
        Updated state with new message
    """
    if role == "human":
        message = HumanMessage(content=content)
    elif role == "ai":
        message = AIMessage(content=content)
    else:
        message = SystemMessage(content=content)
    
    state["messages"].append(message)
    return state


def add_routing_record(
    state: AgentState,
    agent: str,
    reason: str,
    confidence: Optional[float] = None
) -> AgentState:
    """
    Add a routing decision to the history.
    
    Args:
        state: Current agent state
        agent: Name of the selected agent
        reason: Reasoning for the routing decision
        confidence: Confidence score for the routing (0-1)
        
    Returns:
        Updated state with routing record
    """
    routing_record = {
        "agent": agent,
        "reason": reason,
        "confidence": confidence,
        "query": state["query"]
    }
    
    state["routing_history"].append(routing_record)
    return state


def get_conversation_context(state: AgentState, max_messages: int = 5) -> str:
    """
    Get recent conversation context as a formatted string.
    
    Args:
        state: Current agent state
        max_messages: Maximum number of recent messages to include
        
    Returns:
        Formatted conversation context
    """
    messages = state["messages"][-max_messages:] if state["messages"] else []
    
    context_parts = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            context_parts.append(f"User: {msg.content}")
        elif isinstance(msg, AIMessage):
            context_parts.append(f"Assistant: {msg.content}")
    
    return "\n".join(context_parts) if context_parts else "No previous context"


def update_metadata(state: AgentState, **kwargs) -> AgentState:
    """
    Update metadata in the state.
    
    Args:
        state: Current agent state
        **kwargs: Metadata fields to update
        
    Returns:
        Updated state with new metadata
    """
    state["metadata"].update(kwargs)
    return state

