"""
Session Management

Manages conversation sessions and their state across multiple requests.
"""

import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict


class SessionManager:
    """
    Manages user sessions and conversation history.
    
    In a production environment, this would use Redis or a database.
    For this proof-of-concept, we use in-memory storage.
    """
    
    def __init__(self, session_timeout_minutes: int = 30):
        """
        Initialize session manager.
        
        Args:
            session_timeout_minutes: Minutes until session expires
        """
        self.sessions: Dict[str, Dict] = {}
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
    
    def get_session(self, session_id: str) -> Dict:
        """
        Get or create a session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Session dictionary
        """
        # Clean up expired sessions
        self._cleanup_expired_sessions()
        
        # Get existing session or create new one
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "session_id": session_id,
                "messages": [],
                "created_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "metadata": {}
            }
        else:
            # Update last activity
            self.sessions[session_id]["last_activity"] = datetime.now().isoformat()
        
        return self.sessions[session_id]
    
    def add_message(self, session_id: str, role: str, content: str) -> None:
        """
        Add a message to the session history.
        
        Args:
            session_id: Session identifier
            role: Message role (human, ai, system)
            content: Message content
        """
        session = self.get_session(session_id)
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        session["messages"].append(message)
        session["last_activity"] = datetime.now().isoformat()
    
    def get_messages(self, session_id: str, limit: Optional[int] = None) -> List[Dict]:
        """
        Get conversation history for a session.
        
        Args:
            session_id: Session identifier
            limit: Maximum number of messages to return (most recent)
            
        Returns:
            List of messages
        """
        session = self.get_session(session_id)
        messages = session.get("messages", [])
        
        if limit:
            return messages[-limit:]
        
        return messages
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if deleted, False if not found
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def list_sessions(self) -> List[Dict]:
        """
        List all active sessions.
        
        Returns:
            List of session metadata
        """
        self._cleanup_expired_sessions()
        
        return [
            {
                "session_id": sid,
                "created_at": session["created_at"],
                "last_activity": session["last_activity"],
                "message_count": len(session.get("messages", []))
            }
            for sid, session in self.sessions.items()
        ]
    
    def _cleanup_expired_sessions(self) -> None:
        """Clean up sessions that have expired."""
        now = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            last_activity = datetime.fromisoformat(session["last_activity"])
            
            if now - last_activity > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
    
    def get_session_count(self) -> int:
        """
        Get the number of active sessions.
        
        Returns:
            Number of sessions
        """
        self._cleanup_expired_sessions()
        return len(self.sessions)
    
    def clear_all_sessions(self) -> None:
        """Clear all sessions (useful for testing)."""
        self.sessions.clear()

