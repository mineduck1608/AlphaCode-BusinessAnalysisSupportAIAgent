"""Chat agent for Requirements Engineering Assistant."""

import asyncio
import json
from datetime import datetime
from typing import Optional, List

from api.websocket.agents.base_agent import BaseAgent
from api.core.models import Message
from api.services.conversation import ConversationService
from api.core.db import async_session

# Import Google Gemini API
try:
    import google.generativeai as genai
    from api.core.config import settings
    
    GENAI_API_KEY = settings.GENAI_API_KEY
    MODEL = settings.LLM_MODEL
    
    if GENAI_API_KEY:
        genai.configure(api_key=GENAI_API_KEY)
except Exception as e:
    genai = None
    GENAI_API_KEY = None
    MODEL = None
    print(f"Warning: Could not load Gemini API: {e}")


class ChatAgent(BaseAgent):
    """Requirements Engineering Assistant.
    
    Main use case: Analyze requirements and generate context diagram
    
    Flow:
    1. User inputs requirements (raw text or structured format)
    2. Collect and normalize requirements
    3. Run analysis pipeline
    4. Generate context diagram
    """

    def __init__(self, session_id: str, user_id: Optional[int] = None, agent_id: Optional[int] = None):
        super().__init__(session_id)
        self.user_id = user_id or 1
        self.agent_id = agent_id or 1
        self.conversation_id: Optional[int] = None
        self.conversation_service = ConversationService()
        
        # State
        self.conversation_history = []
        self.collected_requirements: List[str] = []
        self.pipeline_state = "idle"  # idle | collecting | analyzing

    async def initialize_conversation(self, conversation_name: Optional[str] = None):
        """Initialize conversation in database."""
        async with async_session() as db:
            if not self.conversation_id:
                conversation = await self.conversation_service.create_conversation(
                    db=db,
                    name=conversation_name or f"Requirements {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    user_id=self.user_id,
                    is_shared=False
                )
                self.conversation_id = conversation.id
                
                await self.conversation_service.create_conversation_agent(
                    db=db,
                    conversation_id=self.conversation_id,
                    agent_id=self.agent_id,
                    is_active=True
                )

    async def handle_message(self, message: str) -> str:
        """Handle incoming message."""
        if not self.conversation_id:
            await self.initialize_conversation()
        
        # Save user message
        self.conversation_history.append({"role": "user", "content": message})
        await self._save_message(role=1, content=message, user_id=self.user_id)
        
        # Generate response
        response = await self._generate_response(message)
        
        # Save response
        self.conversation_history.append({"role": "assistant", "content": response})
        await self._save_message(role=2, content=response, agent_id=self.agent_id)
        
        return response

    async def _save_message(self, role: int, content: str, user_id: Optional[int] = None, agent_id: Optional[int] = None):
        """Save message to database."""
        async with async_session() as db:
            message = Message(
                role=role,
                content=content,
                content_type=1,
                message_type=1,
                conversation_id=self.conversation_id,
                user_id=user_id,
                agent_id=agent_id,
                created_at=datetime.utcnow(),
                status=1
            )
            db.add(message)
            await db.commit()

    async def _generate_response(self, message: str) -> str:
        """Generate response based on intent."""
        text = message.strip()
        text_lower = text.lower()
        
        # Commands
        if text_lower == "ping":
            return "pong"
        
        if text_lower.startswith("/help"):
            return self._get_help()
        
        if text_lower.startswith("/clear"):
            self.collected_requirements.clear()
            self.pipeline_state = "idle"
            return "✅ Đã xóa requirements."
        
        if text_lower.startswith("/analyze"):
            if not self.collected_requirements:
                return "⚠️ Chưa có requirements. Hãy nhập requirements trước."
            return await self._run_pipeline()
        
        if text_lower.startswith("/collect"):
            self.pipeline_state = "collecting"
            self.collected_requirements.clear()
            return "📝 Bắt đầu thu thập requirements. Nhập requirements và gõ /done khi xong."
        
        if text_lower.startswith("/done") and self.pipeline_state == "collecting":
            self.pipeline_state = "idle"
            if not self.collected_requirements:
                return "⚠️ Chưa có requirements."
            return await self._run_pipeline()
        
        # Check if message is requirement
        if self._is_requirement(text):
            self.collected_requirements.append(text)
            count = len(self.collected_requirements)
            return f"✅ Đã lưu requirement #{count}. Gõ /analyze để phân tích."
        
        # General chat
        if genai and GENAI_API_KEY:
            return await self._call_gemini(text)
        
        return "Tôi là Requirements Assistant. Nhập requirements để phân tích. Gõ /help để xem hướng dẫn."

    def _is_requirement(self, text: str) -> bool:
        """Check if text is a requirement."""
        text_lower = text.lower()
        patterns = [
            "story:", "as a ", "as an ", "given ", "when ", "then ",
            "acceptance criteria:", "requirement:", "the system shall",
            "the system must", "the user can", "the user should"
        ]
        
        if self.pipeline_state == "collecting":
            return True
        
        return any(p in text_lower for p in patterns)

    async def _run_pipeline(self) -> str:
        """Run requirements analysis pipeline using MCP servers."""
        try:
            self.pipeline_state = "analyzing"
            raw_text = "\n\n".join(self.collected_requirements)
            reqs_count = len(self.collected_requirements)
            
            # Import MCP adapter
            from api.services import mcp_adapter
            
            # Step 1: Collector - ingest raw text
            ing_resp = await asyncio.to_thread(
                mcp_adapter.call_mcp,
                "mcp_collector",
                "ingest_raw",
                {"items": [raw_text]}
            )
            
            if ing_resp.get("error"):
                return f"❌ Lỗi Collector (ingest): {ing_resp.get('error')}"
            
            chunks = ing_resp.get("response", {}).get("chunks") or ing_resp.get("chunks") or []
            
            # Step 2: Collector - normalize chunks
            norm_resp = await asyncio.to_thread(
                mcp_adapter.call_mcp,
                "mcp_collector",
                "normalize",
                {"chunks": chunks}
            )
            
            if norm_resp.get("error"):
                return f"❌ Lỗi Collector (normalize): {norm_resp.get('error')}"
            
            norm_chunks = norm_resp.get("response", {}).get("chunks") or norm_resp.get("chunks") or []
            
            # Step 3: Collector - extract stories
            ext_resp = await asyncio.to_thread(
                mcp_adapter.call_mcp,
                "mcp_collector",
                "extract_stories",
                {"chunks": norm_chunks}
            )
            
            if ext_resp.get("error"):
                return f"❌ Lỗi Collector (extract): {ext_resp.get('error')}"
            
            stories = ext_resp.get("response", {}).get("stories") or ext_resp.get("stories") or []
            
            # Step 4: Analyzer - analyze stories
            anl_resp = await asyncio.to_thread(
                mcp_adapter.call_mcp,
                "mcp_analyzer",
                "analyze_stories",
                {"stories": stories}
            )
            
            if anl_resp.get("error"):
                return f"❌ Lỗi Analyzer: {anl_resp.get('error')}"
            
            analysis = anl_resp.get("response", {}) or anl_resp
            
            # Step 5: Requirement - identify requirements
            idr_resp = await asyncio.to_thread(
                mcp_adapter.call_mcp,
                "mcp_requirement",
                "identify_requirements",
                {"stories": stories, "analysis": analysis}
            )
            
            if idr_resp.get("error"):
                return f"❌ Lỗi Requirement (identify): {idr_resp.get('error')}"
            
            requirements = idr_resp.get("response", {}).get("requirements") or idr_resp.get("requirements") or []
            
            # Step 6: Requirement - prioritize
            pri_resp = await asyncio.to_thread(
                mcp_adapter.call_mcp,
                "mcp_requirement",
                "prioritize",
                {"requirements": requirements}
            )
            
            if pri_resp.get("error"):
                return f"❌ Lỗi Requirement (prioritize): {pri_resp.get('error')}"
            
            prioritized = pri_resp.get("response", {}) or pri_resp
            
            # Step 7: Reporter - build final report with context diagram
            rep_resp = await asyncio.to_thread(
                mcp_adapter.call_mcp,
                "mcp_reporter",
                "build_final_report",
                {
                    "core_requirements": requirements,
                    "analyzer_output": analysis,
                    "project_id": f"project_{self.conversation_id}"
                }
            )
            
            if rep_resp.get("error"):
                return f"❌ Lỗi Reporter: {rep_resp.get('error')}"
            
            report = rep_resp.get("response") or rep_resp
            
            # Extract results
            self.pipeline_state = "idle"
            stories_count = len(stories)
            reqs_count = len(requirements)
            
            # Get mermaid diagram from report
            mermaid_diagram = report.get("final_report_mermaid", "")
            markdown_report = report.get("final_report_markdown", "")
            
            # Format result
            result = f"""✅ Pipeline phân tích hoàn tất!

📊 Kết quả:
• {reqs_count} requirements ban đầu
• {stories_count} stories được trích xuất
• {len(requirements)} core requirements được xác định

📈 Context Diagram:
```mermaid
{mermaid_diagram}
```

� Executive Summary:
{markdown_report[:500]}...

�💾 Đã lưu vào conversation #{self.conversation_id}
"""
            
            # Save full pipeline result to DB
            await self._save_message(
                role=3,
                content=json.dumps({
                    "type": "pipeline_result",
                    "project_id": f"project_{self.conversation_id}",
                    "collector": {
                        "chunks": len(chunks),
                        "normalized_chunks": len(norm_chunks),
                        "stories": stories
                    },
                    "analyzer": analysis,
                    "requirements": requirements,
                    "prioritized": prioritized,
                    "report": report
                }),
                agent_id=self.agent_id
            )
            
            return result
            
        except Exception as e:
            import traceback
            self.pipeline_state = "idle"
            error_detail = traceback.format_exc()
            return f"❌ Lỗi pipeline: {str(e)}\n\nChi tiết:\n{error_detail[:500]}"

    async def _call_gemini(self, message: str) -> str:
        """Call Gemini API."""
        try:
            system_instruction = """Bạn là Requirements Engineering Assistant.
Giúp người dùng phân tích và viết requirements tốt hơn.
Pipeline: Collector → Analyzer → Requirement → Reporter → Context Diagram"""
            
            model = genai.GenerativeModel(MODEL, system_instruction=system_instruction)
            response = await asyncio.to_thread(model.generate_content, message)
            
            if hasattr(response, 'text'):
                return response.text
            return str(response)
        except Exception as e:
            return f"❌ Lỗi Gemini: {str(e)}"

    def _get_help(self) -> str:
        """Return help text."""
        return """🤖 Requirements Engineering Assistant

📝 Nhập Requirements:
• Story: [Title]
• As a [role], I want [feature]
• Given [context] When [action] Then [result]

🔧 Commands:
• /collect - Bắt đầu thu thập
• /analyze - Phân tích requirements
• /done - Kết thúc và phân tích
• /clear - Xóa requirements
• /help - Hiển thị help

🔄 Pipeline:
Collector → Analyzer → Requirement → Reporter → Diagram"""
