"""Chat agent implementation for handling user conversations."""

import asyncio
from datetime import datetime
from gateway.agents.base_agent import BaseAgent


class ChatAgent(BaseAgent):
    """AI chat agent that processes messages and maintains conversation history.
    
    This agent demonstrates how to:
    - Maintain conversation context
    - Process different message types
    - Generate responses with typing simulation
    """

    def __init__(self, session_id: str):
        super().__init__(session_id)
        self.conversation_history = []
        self.user_name = "User"

    async def handle_message(self, message: str) -> str:
        """Process incoming message and generate response.
        
        Args:
            message: User's input message
            
        Returns:
            Agent's response text
        """
        # Store user message
        self.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })

        # Parse message and generate response
        response = await self._generate_response(message)

        # Store agent response
        self.conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })

        return response

    async def _generate_response(self, message: str) -> str:
        """Generate response based on message content.
        
        Args:
            message: User's message
            
        Returns:
            Generated response
        """
        text = message.strip().lower()

        # Handle special commands
        if text == "ping":
            return "pong"
        
        if text.startswith("/help"):
            return self._get_help_text()
        
        if text.startswith("/history"):
            return self._get_history()
        
        if text.startswith("/clear"):
            self.conversation_history.clear()
            return "Conversation history cleared."
        
        if text.startswith("/whoami"):
            return f"Session ID: {self.session_id}\nConversation messages: {len(self.conversation_history)}"

        # Simulate AI processing delay
        await asyncio.sleep(0.1)

        # Generate response based on message content
        if "hello" in text or "hi" in text:
            return f"Hello! How can I assist you today? (Session: {self.session_id[:8]}...)"
        
        if "how are you" in text:
            return "I'm functioning perfectly! Ready to help you with any questions."
        
        if "time" in text:
            return f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Default response with echo
        return f"I received your message: '{message}'. This is a demo response from the AI agent."

    def _get_help_text(self) -> str:
        """Return help text with available commands."""
        return """Available commands:
/help - Show this help message
/history - Show conversation history
/clear - Clear conversation history
/whoami - Show session information
ping - Test connection

You can also send any message and I'll respond!"""

    def _get_history(self) -> str:
        """Return formatted conversation history."""
        if not self.conversation_history:
            return "No conversation history yet."
        
        history_text = "Conversation History:\n" + "="*50 + "\n"
        for idx, msg in enumerate(self.conversation_history[-10:], 1):  # Last 10 messages
            role = "You" if msg["role"] == "user" else "Agent"
            history_text += f"{idx}. [{role}]: {msg['content'][:100]}\n"
        
        return history_text
