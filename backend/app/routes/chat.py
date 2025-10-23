"""
Chat API Endpoint

Provides the /chat endpoint for interacting with the multi-agent system.
Supports both streaming and non-streaming responses.
"""

import json
import uuid
from typing import Optional, Dict, List
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.graph.orchestrator import process_query, process_query_with_streaming
from app.sessions import SessionManager


router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., description="User's message/query", min_length=1)
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    stream: bool = Field(True, description="Enable streaming responses")


class ChatResponse(BaseModel):
    """Response model for non-streaming chat."""
    response: str = Field(..., description="Agent's response")
    agent: str = Field(..., description="Which agent handled the query")
    strategy: str = Field(..., description="Retrieval strategy used")
    session_id: str = Field(..., description="Session identifier")
    processing_time: float = Field(..., description="Processing time in seconds")
    success: bool = Field(..., description="Whether the request was successful")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")


# Global session manager
session_manager = SessionManager()

# Agent name mapping
AGENT_NAME_MAP = {
    "billing": "Billing Support",
    "technical": "Technical Support",
    "policy": "Policy & Compliance"
}


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - handles user queries through the multi-agent system.
    
    Supports both streaming and non-streaming modes:
    - Streaming (default): Returns Server-Sent Events stream
    - Non-streaming: Returns complete JSON response
    
    Args:
        request: ChatRequest with message, session_id, and stream flag
        
    Returns:
        StreamingResponse for streaming mode, ChatResponse for non-streaming
    """
    try:
        # Generate session ID if not provided
        if not request.session_id:
            request.session_id = str(uuid.uuid4())
        
        # Get or create session
        session = session_manager.get_session(request.session_id)
        
        # Get conversation history
        messages = session.get("messages", [])
        
        # Streaming response
        if request.stream:
            async def generate_stream():
                """Generate SSE stream for the response."""
                try:
                    # Send session info first
                    yield f"data: {json.dumps({'type': 'session', 'session_id': request.session_id})}\n\n"
                    
                    # Get agent metadata first
                    from app.graph.orchestrator import get_orchestrator
                    from app.graph.state import create_initial_state
                    
                    # Create initial state to get routing decision
                    state = create_initial_state(
                        query=request.message,
                        session_id=request.session_id
                    )
                    orchestrator = get_orchestrator()
                    state = orchestrator.route_query(state)
                    
                    # Send agent metadata (convert to friendly name)
                    agent_key = state["selected_agent"]
                    agent_name = AGENT_NAME_MAP.get(agent_key, agent_key)
                    agent_data = {
                        "type": "agent",
                        "agent": agent_name,
                        "confidence": state.get("routing_history", [{}])[-1].get("confidence", 0)
                    }
                    yield f"data: {json.dumps(agent_data)}\n\n"
                    
                    # Stream the response
                    full_response = ""
                    async for chunk in process_query_with_streaming(
                        query=request.message,
                        session_id=request.session_id,
                        messages=messages
                    ):
                        full_response += chunk
                        
                        # Send chunk
                        data = {
                            "type": "chunk",
                            "content": chunk
                        }
                        yield f"data: {json.dumps(data)}\n\n"
                    
                    # Update session with new messages
                    session_manager.add_message(request.session_id, "human", request.message)
                    session_manager.add_message(request.session_id, "ai", full_response)
                    
                    # Send completion event
                    completion_data = {
                        "type": "done",
                        "message": "Stream completed"
                    }
                    yield f"data: {json.dumps(completion_data)}\n\n"
                
                except Exception as e:
                    error_data = {
                        "type": "error",
                        "error": str(e)
                    }
                    yield f"data: {json.dumps(error_data)}\n\n"
            
            return StreamingResponse(
                generate_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"
                }
            )
        
        # Non-streaming response
        else:
            result = process_query(
                query=request.message,
                session_id=request.session_id,
                messages=messages
            )
            
            # Update session
            session_manager.add_message(request.session_id, "human", request.message)
            session_manager.add_message(request.session_id, "ai", result["response"])
            
            # Map agent name to friendly name
            agent_name = AGENT_NAME_MAP.get(result["agent"], result["agent"])
            
            return ChatResponse(
                response=result["response"],
                agent=agent_name,
                strategy=result["strategy"],
                session_id=request.session_id,
                processing_time=result["processing_time"],
                success=result["success"]
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        )


@router.get("/chat/sessions/{session_id}")
async def get_session(session_id: str):
    """
    Get session information and conversation history.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Session data including message history
    """
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "messages": session.get("messages", []),
        "created_at": session.get("created_at"),
        "last_activity": session.get("last_activity"),
        "message_count": len(session.get("messages", []))
    }


@router.delete("/chat/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a session and its conversation history.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Success message
    """
    success = session_manager.delete_session(session_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "message": "Session deleted successfully",
        "session_id": session_id
    }


@router.get("/chat/sessions")
async def list_sessions():
    """
    List all active sessions.
    
    Returns:
        List of session IDs with metadata
    """
    sessions = session_manager.list_sessions()
    
    return {
        "sessions": sessions,
        "count": len(sessions)
    }


@router.post("/chat/test")
async def test_agent_routing(request: ChatRequest):
    """
    Test endpoint to see which agent would handle a query without executing it.
    Useful for debugging routing decisions.
    
    Args:
        request: ChatRequest with message
        
    Returns:
        Routing information
    """
    from app.graph.orchestrator import get_orchestrator
    from app.graph.state import create_initial_state
    
    try:
        # Create initial state
        state = create_initial_state(
            query=request.message,
            session_id=request.session_id or "test"
        )
        
        # Get routing decision
        orchestrator = get_orchestrator()
        state = orchestrator.route_query(state)
        
        return {
            "query": request.message,
            "selected_agent": state["selected_agent"],
            "routing_history": state["routing_history"],
            "message": f"This query would be routed to: {state['selected_agent']}"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error testing routing: {str(e)}"
        )

