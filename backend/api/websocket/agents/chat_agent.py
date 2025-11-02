"""Chat agent implementation for handling user conversations."""

import asyncio
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from api.websocket.agents.base_agent import BaseAgent
from api.core.models import Conversation, Message
from api.services.conversation import ConversationService
from api.core.db import async_session


class ChatAgent(BaseAgent):
    """AI chat agent that processes messages and maintains conversation history.
    
    This agent demonstrates how to:
    - Maintain conversation context
    - Process different message types
    - Generate responses with typing simulation
    - Save messages to database
    """

    def __init__(self, session_id: str, user_id: Optional[int] = None, agent_id: Optional[int] = None):
        super().__init__(session_id)
        self.conversation_history = []
        self.user_name = "User"
        self.user_id = user_id or 1  # Default user ID, should be from auth
        self.agent_id = agent_id or 1  # Default agent ID
        self.conversation_id: Optional[int] = None
        self.conversation_service = ConversationService()

    async def initialize_conversation(self, conversation_name: Optional[str] = None):
        """Initialize or get existing conversation for this session."""
        async with async_session() as db:
            # Create new conversation if not exists
            if not self.conversation_id:
                conversation = await self.conversation_service.create_conversation(
                    db=db,
                    name=conversation_name or f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    user_id=self.user_id,
                    is_shared=False
                )
                self.conversation_id = conversation.id
                
                # Link agent to conversation
                await self.conversation_service.create_conversation_agent(
                    db=db,
                    conversation_id=self.conversation_id,
                    agent_id=self.agent_id,
                    is_active=True
                )

    async def handle_message(self, message: str) -> str:
        """Process incoming message and generate response.
        
        Args:
            message: User's input message
            
        Returns:
            Agent's response text
        """
        # Initialize conversation if needed
        if not self.conversation_id:
            await self.initialize_conversation()
        
        # Store user message in memory
        self.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })

        # Save user message to database
        await self._save_message(
            role=1,  # 1 = user
            content=message,
            content_type=1,  # 1 = text
            message_type=1,  # 1 = normal message
            user_id=self.user_id
        )

        # Parse message and generate response
        response = await self._generate_response(message)

        # Store agent response in memory
        self.conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })

        # Save agent response to database
        await self._save_message(
            role=2,  # 2 = assistant
            content=response,
            content_type=1,  # 1 = text
            message_type=1,  # 1 = normal message
            agent_id=self.agent_id
        )

        return response

    async def _save_message(
        self,
        role: int,
        content: str,
        content_type: int,
        message_type: int,
        user_id: Optional[int] = None,
        agent_id: Optional[int] = None
    ):
        """Save message to database."""
        async with async_session() as db:
            message = Message(
                role=role,
                content=content,
                content_type=content_type,
                message_type=message_type,
                conversation_id=self.conversation_id,
                user_id=user_id,
                agent_id=agent_id,
                created_at=datetime.utcnow(),
                status=1
            )
            db.add(message)
            await db.commit()

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
