"""Session manager for tracking WebSocket connections and agent instances."""

from typing import Dict, Optional
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages active WebSocket sessions and their associated agents.
    
    This class tracks all active connections and provides methods to:
    - Register new sessions
    - Unregister closed sessions
    - Broadcast messages to all or specific sessions
    - Retrieve session information
    """

    def __init__(self):
        """Initialize empty session storage."""
        self.active_sessions: Dict[str, Dict] = {}

    def register(self, session_id: str, websocket: WebSocket, agent):
        """Register a new WebSocket session with its agent.
        
        Args:
            session_id: Unique session identifier
            websocket: WebSocket connection instance
            agent: Agent instance for this session
        """
        self.active_sessions[session_id] = {
            "websocket": websocket,
            "agent": agent,
            "connected": True
        }
        logger.info(f"Session registered: {session_id}. Total active: {len(self.active_sessions)}")

    def unregister(self, session_id: str):
        """Unregister a session when connection closes.
        
        Args:
            session_id: Session identifier to remove
        """
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            logger.info(f"Session unregistered: {session_id}. Total active: {len(self.active_sessions)}")

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data dict or None if not found
        """
        return self.active_sessions.get(session_id)

    async def broadcast(self, message: str, exclude_session: Optional[str] = None):
        """Broadcast a message to all active sessions.
        
        Args:
            message: Message to broadcast
            exclude_session: Optional session ID to exclude from broadcast
        """
        disconnected = []
        for session_id, session_data in self.active_sessions.items():
            if exclude_session and session_id == exclude_session:
                continue
            
            try:
                await session_data["websocket"].send_text(message)
            except Exception as e:
                logger.error(f"Failed to send to {session_id}: {e}")
                disconnected.append(session_id)
        
        # Clean up disconnected sessions
        for session_id in disconnected:
            self.unregister(session_id)

    async def send_to_session(self, session_id: str, message: str) -> bool:
        """Send a message to a specific session.
        
        Args:
            session_id: Target session ID
            message: Message to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        try:
            await session["websocket"].send_text(message)
            return True
        except Exception as e:
            logger.error(f"Failed to send to {session_id}: {e}")
            self.unregister(session_id)
            return False

    def get_active_count(self) -> int:
        """Get count of active sessions.
        
        Returns:
            Number of active sessions
        """
        return len(self.active_sessions)
