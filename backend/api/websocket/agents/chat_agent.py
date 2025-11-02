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
        """Generate response based on message content using Gemini API.
        
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

        # Check if message contains requirements/stories - route to pipeline
        # User can mention "Story:" or ask about requirements analysis
        if "story:" in message.lower() or "/analyze" in text or "/pipeline" in text:
            return await self._handle_requirements_analysis(message)

        # Use Gemini API for chat if available
        if genai and GENAI_API_KEY:
            return await self._call_gemini(message)
        
        # Fallback responses if Gemini not available
        await asyncio.sleep(0.1)
        
        if "hello" in text or "hi" in text:
            return f"Hello! I'm your Requirements Engineering Assistant. How can I help you today?"
        
        if "how are you" in text:
            return "I'm functioning perfectly! I can help you analyze requirements, detect issues, and generate reports."
        
        if "time" in text:
            return f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Default fallback
        return f"Tôi đã nhận được tin nhắn của bạn: '{message}'. Để sử dụng Gemini API, vui lòng cấu hình GENAI_API_KEY trong file .env"
    
    async def _handle_requirements_analysis(self, message: str) -> str:
        """Handle requirements analysis via pipeline.
        
        Args:
            message: User message containing requirements/stories
            
        Returns:
            Response about pipeline analysis
        """
        # Import pipeline function and request model
        try:
            from api.routers.mcp import run_pipeline, PipelineRequest
            
            # Check if message contains raw text or structured stories
            if "story:" in message.lower():
                # Create request object for pipeline
                pipeline_request = PipelineRequest(
                    raw_text=message,
                    project_id="default",
                    stories=None
                )
                
                # Call pipeline in thread (it's a sync function)
                pipeline_result = await asyncio.to_thread(
                    run_pipeline,
                    pipeline_request
                )
                
                if pipeline_result.get("ok"):
                    stories_count = len(pipeline_result.get("stories", []))
                    reqs_count = len(pipeline_result.get("requirements", []))
                    analysis_raw = pipeline_result.get("analysis", {})
                    analysis = analysis_raw.get("analysis", analysis_raw) if isinstance(analysis_raw, dict) else analysis_raw
                    issues_count = analysis.get("summary", {}).get("total_issues", 0) if isinstance(analysis, dict) else 0
                    
                    return f"""✅ Pipeline phân tích hoàn tất!

📊 Kết quả:
• {stories_count} story được phát hiện
• {reqs_count} requirements được tạo
• {issues_count} vấn đề được phát hiện

Bạn có thể xem chi tiết trong Preview Panel hoặc gọi API /mcp/pipeline để lấy full report."""
                else:
                    return f"❌ Lỗi khi chạy pipeline: {pipeline_result.get('error', 'Unknown error')}"
            else:
                return "Để phân tích requirements, hãy nhập với format:\nStory: [Title]\n[Description]\nAcceptance Criteria:\n- [Criteria]"
        except Exception as e:
            import traceback
            return f"❌ Lỗi khi xử lý requirements analysis: {str(e)}\n{traceback.format_exc()}"
    
    async def _call_gemini(self, message: str) -> str:
        """Call Gemini API to generate response.
        
        Args:
            message: User message
            
        Returns:
            Generated response from Gemini
        """
        try:
            # Build system instruction
            system_instruction = """Bạn là Requirements Engineering Assistant, một AI chuyên gia trong việc phân tích và quản lý software requirements.

Nhiệm vụ của bạn:
- Trả lời câu hỏi về requirements engineering
- Hướng dẫn người dùng sử dụng hệ thống
- Giải thích về các agents (Collector, Analyzer, Requirement, Reporter)
- Tư vấn về best practices trong requirements engineering

Nếu người dùng muốn phân tích requirements, hướng dẫn họ nhập với format:
Story: [Title]
[Description]
Acceptance Criteria:
- [Criteria]

Hãy trả lời một cách thân thiện, chuyên nghiệp và hữu ích."""
            
            # Build chat history for context
            chat_history = []
            for msg in self.conversation_history[-10:]:
                role = "user" if msg["role"] == "user" else "model"
                chat_history.append({"role": role, "parts": [msg["content"]]})
            
            # Create model with system instruction
            model = genai.GenerativeModel(
                MODEL,
                system_instruction=system_instruction
            )
            
            # Start chat if we have history, otherwise single message
            if chat_history:
                # Use chat interface for multi-turn conversation
                chat = model.start_chat(history=chat_history)
                response = await asyncio.to_thread(
                    chat.send_message,
                    message
                )
            else:
                # Single message
                response = await asyncio.to_thread(
                    model.generate_content,
                    message
                )
            
            # Extract text from response
            if hasattr(response, 'text'):
                return response.text
            elif hasattr(response, 'candidates') and response.candidates:
                if hasattr(response.candidates[0], 'content'):
                    parts = response.candidates[0].content.parts
                    if parts and hasattr(parts[0], 'text'):
                        return parts[0].text
                return str(response.candidates[0])
            else:
                return str(response)
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            return f"❌ Lỗi khi gọi Gemini API: {str(e)}\n\nVui lòng kiểm tra:\n1. GENAI_API_KEY đã được cấu hình trong .env\n2. API key có hợp lệ không\n3. Model {MODEL} có sẵn không\n\nChi tiết lỗi:\n{error_details[:500]}"

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
