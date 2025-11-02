"""Base agent contract for all agent implementations."""

from typing import Optional, Dict, Any


class BaseAgent:
    """Base class for all agents.
    
    Agents handle incoming messages from users and produce responses
    that can be streamed back to the UI via WebSocket.
    """

    def __init__(self, session_id: str):
        """Initialize agent with a unique session ID.
        
        Args:
            session_id: Unique identifier for this agent session
        """
        self.session_id = session_id
        self.context: Dict[str, Any] = {}

    async def handle_message(self, message: str) -> str:
        """Process an incoming message and return a response.
        
        Args:
            message: The user's message text
            
        Returns:
            Response text to send back to the user
        """
        raise NotImplementedError("Subclasses must implement handle_message")

    async def stream_response(self, message: str):
        """Stream response chunks (for future streaming support).
        
        Args:
            message: The user's message text
            
        Yields:
            Response chunks
        """
        # Default implementation: return full response at once
        response = await self.handle_message(message)
        yield response
