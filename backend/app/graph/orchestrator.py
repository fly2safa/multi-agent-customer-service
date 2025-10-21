"""
LangGraph Orchestrator - Intelligent Query Routing

This module implements the orchestrator that analyzes user queries
and routes them to the appropriate specialized agent using LangGraph.
"""

import time
from typing import Dict, List, Optional, Literal
from langgraph.graph import StateGraph, END
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.llm_providers import get_orchestrator_llm
from app.agents import BillingAgent, TechnicalAgent, PolicyAgent
from app.graph.state import AgentState, add_message, add_routing_record, update_metadata


class AgentOrchestrator:
    """
    Orchestrator for the multi-agent customer service system.
    
    Uses AWS Bedrock Claude 3.5 Haiku for fast, cost-effective routing
    and coordinates between three specialized worker agents.
    """
    
    def __init__(self):
        """Initialize the orchestrator and worker agents."""
        # LLM for routing decisions (Bedrock Claude - fast and cheap)
        self.routing_llm = get_orchestrator_llm()
        
        # Initialize specialized worker agents
        self.billing_agent = BillingAgent()
        self.technical_agent = TechnicalAgent()
        self.policy_agent = PolicyAgent()
        
        # Agent mapping
        self.agents = {
            "billing": self.billing_agent,
            "technical": self.technical_agent,
            "policy": self.policy_agent
        }
        
        # Routing prompt
        self.routing_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a routing specialist for a customer service system. 
Your job is to analyze customer queries and determine which specialized agent should handle them.

Available agents:
1. BILLING - Handles questions about pricing, plans, invoices, payments, subscriptions, upgrades/downgrades
2. TECHNICAL - Handles technical support, troubleshooting, account setup, API issues, authentication, webhooks
3. POLICY - Handles questions about terms of service, privacy policy, GDPR, data retention, compliance, legal matters

Analyze the query and respond with ONLY the agent name (billing, technical, or policy) in lowercase.
If the query is ambiguous, choose the most likely agent based on keywords and context."""),
            ("human", "Query: {query}\n\nWhich agent should handle this? Respond with only: billing, technical, or policy")
        ])
    
    def route_query(self, state: AgentState) -> AgentState:
        """
        Analyze the query and route to appropriate agent.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with selected_agent set
        """
        query = state["query"]
        
        # Use routing LLM to determine the best agent
        chain = self.routing_prompt | self.routing_llm | StrOutputParser()
        
        try:
            # Get routing decision
            routing_decision = chain.invoke({"query": query}).strip().lower()
            
            # Validate routing decision
            if routing_decision not in ["billing", "technical", "policy"]:
                # Default to technical if unclear
                routing_decision = "technical"
            
            # Update state
            state["selected_agent"] = routing_decision
            
            # Add routing record
            add_routing_record(
                state,
                agent=routing_decision,
                reason=f"Query classified as {routing_decision}-related",
                confidence=0.9
            )
            
            return state
        
        except Exception as e:
            # Fallback routing on error
            state["selected_agent"] = "technical"
            state["error"] = f"Routing error: {str(e)}"
            
            add_routing_record(
                state,
                agent="technical",
                reason="Fallback due to routing error",
                confidence=0.5
            )
            
            return state
    
    def call_agent(self, state: AgentState) -> AgentState:
        """
        Call the selected agent to process the query.
        
        Args:
            state: Current agent state with selected_agent set
            
        Returns:
            Updated state with agent response
        """
        agent_name = state["selected_agent"]
        query = state["query"]
        session_id = state["session_id"]
        
        # Get the appropriate agent
        agent = self.agents.get(agent_name)
        
        if not agent:
            state["response"] = "I apologize, but I'm having trouble routing your question. Please try rephrasing it."
            state["error"] = f"Invalid agent: {agent_name}"
            return state
        
        try:
            # Call the agent
            result = agent.process_query(
                query=query,
                session_id=session_id,
                chat_history=state.get("messages", [])
            )
            
            # Update state with response
            state["response"] = result.get("response", "No response generated")
            
            # Add metadata from agent
            state["metadata"].update({
                "agent": result.get("agent"),
                "strategy": result.get("strategy"),
                "success": result.get("success", True)
            })
            
            # Add response to message history
            add_message(state, "ai", state["response"])
            
            return state
        
        except Exception as e:
            state["response"] = "I apologize, but I encountered an error processing your request. Please try again."
            state["error"] = f"Agent error: {str(e)}"
            return state
    
    async def acall_agent(self, state: AgentState):
        """
        Async version of call_agent with streaming support.
        
        Args:
            state: Current agent state with selected_agent set
            
        Yields:
            Response chunks from the agent
        """
        agent_name = state["selected_agent"]
        query = state["query"]
        session_id = state["session_id"]
        
        agent = self.agents.get(agent_name)
        
        if not agent:
            yield "I apologize, but I'm having trouble routing your question."
            return
        
        try:
            # Stream response from agent
            async for chunk in agent.aprocess_query(
                query=query,
                session_id=session_id,
                chat_history=state.get("messages", [])
            ):
                yield chunk
        
        except Exception as e:
            yield f"I apologize, but I encountered an error: {str(e)}"
    
    def should_end(self, state: AgentState) -> bool:
        """
        Determine if the workflow should end.
        
        Args:
            state: Current agent state
            
        Returns:
            True if workflow should end, False otherwise
        """
        return state.get("response") is not None or state.get("error") is not None


def create_agent_graph() -> StateGraph:
    """
    Create the LangGraph workflow for the multi-agent system.
    
    Returns:
        Compiled StateGraph for orchestration
    """
    # Initialize orchestrator
    orchestrator = AgentOrchestrator()
    
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Define nodes
    workflow.add_node("route", orchestrator.route_query)
    workflow.add_node("call_agent", orchestrator.call_agent)
    
    # Define edges
    workflow.set_entry_point("route")
    workflow.add_edge("route", "call_agent")
    workflow.add_edge("call_agent", END)
    
    # Compile the graph
    return workflow.compile()


# Global graph instance
_graph = None
_orchestrator = None


def get_agent_graph() -> StateGraph:
    """
    Get the compiled agent graph (singleton).
    
    Returns:
        Compiled StateGraph instance
    """
    global _graph
    if _graph is None:
        _graph = create_agent_graph()
    return _graph


def get_orchestrator() -> AgentOrchestrator:
    """
    Get the orchestrator instance (singleton).
    
    Returns:
        AgentOrchestrator instance
    """
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator


async def process_query_with_streaming(
    query: str,
    session_id: str,
    messages: Optional[List] = None
):
    """
    Process a query through the orchestrator with streaming support.
    
    Args:
        query: User's question
        session_id: Unique session identifier
        messages: Previous conversation messages
        
    Yields:
        Streaming response chunks
    """
    from app.graph.state import create_initial_state
    
    # Create initial state
    state = create_initial_state(
        query=query,
        session_id=session_id,
        messages=messages
    )
    
    # Get orchestrator
    orchestrator = get_orchestrator()
    
    # Add timestamp
    state["metadata"]["timestamp"] = time.time()
    
    # Route the query
    state = orchestrator.route_query(state)
    
    # Stream response from selected agent
    async for chunk in orchestrator.acall_agent(state):
        yield chunk
    
    # Update processing time
    state["metadata"]["processing_time"] = time.time() - state["metadata"]["timestamp"]


def process_query(
    query: str,
    session_id: str,
    messages: Optional[List] = None
) -> Dict:
    """
    Process a query through the orchestrator (non-streaming).
    
    Args:
        query: User's question
        session_id: Unique session identifier
        messages: Previous conversation messages
        
    Returns:
        Dictionary with response and metadata
    """
    from app.graph.state import create_initial_state
    
    # Create initial state
    state = create_initial_state(
        query=query,
        session_id=session_id,
        messages=messages
    )
    
    # Add timestamp
    state["metadata"]["timestamp"] = time.time()
    
    # Get and run the graph
    graph = get_agent_graph()
    result_state = graph.invoke(state)
    
    # Update processing time
    result_state["metadata"]["processing_time"] = (
        time.time() - state["metadata"]["timestamp"]
    )
    
    return {
        "response": result_state.get("response"),
        "agent": result_state["metadata"].get("agent"),
        "strategy": result_state["metadata"].get("strategy"),
        "routing_history": result_state.get("routing_history", []),
        "processing_time": result_state["metadata"].get("processing_time"),
        "session_id": session_id,
        "success": not result_state.get("error"),
        "error": result_state.get("error")
    }

