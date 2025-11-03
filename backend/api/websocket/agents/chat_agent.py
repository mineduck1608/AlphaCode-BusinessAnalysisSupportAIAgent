"""Chat agent for Requirements Engineering Assistant."""

import asyncio
import json
import traceback
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
    """Business Analysis Assistant - Chuyên gia phân tích nghiệp vụ và yêu cầu kinh doanh.
    
    🎯 SCOPE: CHỈ hỗ trợ Business Analysis & Use Case Analysis
    
    ✅ Core Capabilities:
    - Phân tích yêu cầu nghiệp vụ (Business Requirements Analysis)
    - Xác định yêu cầu kinh doanh (Business Requirements Specification)
    - Phân tích Use Cases (Use Case Analysis & Modeling)
    - Tạo Context Diagram (System boundary, external actors)
    - Tạo Use Case Diagram (Actors, use cases, relationships)
    - Viết Use Case Specifications (Main flow, alternative flows, preconditions, postconditions)
    - Phân tích Stakeholders (Identify, classify, analyze needs)
    - Phân tích Business Process (As-Is, To-Be process mapping)
    - Requirements Prioritization (MoSCoW, Business Value)
    - Gap Analysis (Current vs Desired state)
    
    ❌ KHÔNG hỗ trợ:
    - Coding/Programming/Development
    - Technical architecture design
    - Database schema design
    - API/Backend implementation
    - Frontend UI/UX design details
    - Infrastructure/DevOps setup
    - Testing automation
    - Project management tasks
    - General chatbot/casual conversation
    
    📋 Main Workflow:
    1. Thu thập business requirements và use cases từ user
    2. Phân tích nghiệp vụ, xác định actors và use cases
    3. Tìm conflicts, gaps, ambiguity trong requirements
    4. Ưu tiên requirements theo business value
    5. Tạo Context Diagram + Use Case Diagram
    6. Generate Use Case Specifications
    7. Lưu analysis vào DB với embeddings để recall
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
        
        # Pipeline results cache for summary generation
        self.last_pipeline_result = {
            "stories": [],
            "analysis": {},
            "requirements": [],
            "validation_issues": [],
            "diagram": "",
            "report": {}
        }

    async def initialize_conversation(self, conversation_name: Optional[str] = None):
        """Initialize conversation in database and load existing context."""
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
            else:
                # Load existing conversation context
                await self._load_conversation_context(db)

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
    
    async def _load_conversation_context(self, db):
        """Load existing conversation context from DB."""
        conversation = await self.conversation_service.get_conversation_by_id(db, self.conversation_id)
        if conversation and conversation.summary:
            # Parse summary to restore pipeline results if available
            try:
                # Summary format: "Analysis: {json}"
                if "Requirements:" in conversation.summary:
                    # Context exists, could be parsed but for now just note it exists
                    pass
            except Exception:
                pass
    
    async def _save_conversation_summary(self, summary: str, embedding: Optional[List[float]] = None):
        """Save conversation summary and embedding to DB."""
        async with async_session() as db:
            conversation = await self.conversation_service.get_conversation_by_id(db, self.conversation_id)
            if conversation:
                conversation.summary = summary
                if embedding:
                    conversation.summary_embedding = embedding
                conversation.last_updated = datetime.utcnow()
                db.add(conversation)
                await db.commit()
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using Gemini API."""
        try:
            if not genai or not GENAI_API_KEY:
                return []
            
            # Use Gemini embedding API
            result = await asyncio.to_thread(
                genai.embed_content,
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            
            return result['embedding']
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []
    
    async def _search_similar_conversations(self, query: str, top_k: int = 5):
        """Search similar conversations using embeddings."""
        try:
            # Generate query embedding
            query_embedding = await self._generate_embedding(query)
            if not query_embedding:
                return []
            
            # Search in DB using cosine similarity
            # TODO: Implement vector similarity search in PostgreSQL with pgvector
            # For now, return empty
            return []
        except Exception as e:
            print(f"Error searching conversations: {e}")
            return []

    async def _generate_response(self, message: str) -> str:
        """Generate response using Gemini as orchestrator."""
        text = message.strip()
        text_lower = text.lower()
        
        # Only handle ping command
        if text_lower == "ping":
            return "pong"
        
        # Use Gemini to understand intent and route to appropriate action
        if genai and GENAI_API_KEY:
            return await self._call_gemini_orchestrator(text)
        
        return "Xin lỗi, tôi đang gặp vấn đề kết nối với AI. Vui lòng thử lại."

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

    async def _call_gemini_orchestrator(self, message: str) -> str:
        """Call Gemini as orchestrator with function calling for MCP routing."""
        try:
            # Define function declarations matching MCP servers capabilities
            
            # Collector MCP functions
            ingest_raw_declaration = genai.protos.FunctionDeclaration(
                name="ingest_raw_requirements",
                description="Thu thập và chuẩn hóa raw requirements từ user input. Tự động gọi khi user nhập requirements.",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "items": genai.protos.Schema(
                            type=genai.protos.Type.ARRAY,
                            items=genai.protos.Schema(type=genai.protos.Type.STRING),
                            description="Raw requirement text items"
                        )
                    },
                    required=["items"]
                )
            )
            
            # Analyzer MCP functions
            analyze_declaration = genai.protos.FunctionDeclaration(
                name="analyze_stories",
                description="Phân tích stories để tìm issues, conflicts, suggestions. Gọi sau khi có stories từ collector.",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "stories": genai.protos.Schema(
                            type=genai.protos.Type.ARRAY,
                            items=genai.protos.Schema(type=genai.protos.Type.OBJECT),
                            description="User stories cần phân tích"
                        )
                    },
                    required=["stories"]
                )
            )
            
            # Requirement MCP functions
            identify_declaration = genai.protos.FunctionDeclaration(
                name="identify_requirements",
                description="Xác định và tổng hợp core requirements từ analyzed stories.",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "stories": genai.protos.Schema(
                            type=genai.protos.Type.ARRAY,
                            items=genai.protos.Schema(type=genai.protos.Type.OBJECT),
                            description="Stories đã được analyze"
                        )
                    },
                    required=["stories"]
                )
            )
            
            prioritize_declaration = genai.protos.FunctionDeclaration(
                name="prioritize_requirements",
                description="Ưu tiên các requirements theo độ quan trọng và urgency.",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "requirements": genai.protos.Schema(
                            type=genai.protos.Type.ARRAY,
                            items=genai.protos.Schema(type=genai.protos.Type.OBJECT),
                            description="Requirements cần prioritize"
                        )
                    },
                    required=["requirements"]
                )
            )
            
            # Reporter MCP function
            generate_report_declaration = genai.protos.FunctionDeclaration(
                name="generate_context_diagram",
                description="Tạo context diagram (Mermaid) từ prioritized requirements. Gọi cuối cùng để tạo visualization.",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "requirements": genai.protos.Schema(
                            type=genai.protos.Type.ARRAY,
                            items=genai.protos.Schema(type=genai.protos.Type.OBJECT),
                            description="Prioritized requirements"
                        )
                    },
                    required=["requirements"]
                )
            )
            
            # Validator MCP functions
            validate_req_declaration = genai.protos.FunctionDeclaration(
                name="validate_requirements",
                description="Validate requirements structure và completeness. Gọi sau khi prioritize để đảm bảo quality.",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "requirements": genai.protos.Schema(
                            type=genai.protos.Type.ARRAY,
                            items=genai.protos.Schema(type=genai.protos.Type.OBJECT),
                            description="Requirements cần validate"
                        )
                    },
                    required=["requirements"]
                )
            )
            
            # Vector MCP functions - for conversation context storage
            store_context_declaration = genai.protos.FunctionDeclaration(
                name="store_conversation_context",
                description="Lưu conversation context vào vector store để có thể retrieve sau này. Tự động gọi sau khi hoàn thành pipeline.",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "summary": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            description="Summary của conversation"
                        ),
                        "requirements": genai.protos.Schema(
                            type=genai.protos.Type.ARRAY,
                            items=genai.protos.Schema(type=genai.protos.Type.OBJECT),
                            description="Requirements đã xử lý"
                        ),
                        "diagram": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            description="Context diagram đã tạo"
                        )
                    },
                    required=["summary"]
                )
            )
            
            search_context_declaration = genai.protos.FunctionDeclaration(
                name="search_previous_context",
                description="Tìm kiếm previous conversation context từ vector store khi user hỏi về requirements trước đó.",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "query": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            description="Search query"
                        ),
                        "top_k": genai.protos.Schema(
                            type=genai.protos.Type.INTEGER,
                            description="Number of results"
                        )
                    },
                    required=["query"]
                )
            )
            
            # Utility functions
            help_declaration = genai.protos.FunctionDeclaration(
                name="show_help",
                description="Hiển thị hướng dẫn sử dụng chi tiết",
                parameters=genai.protos.Schema(type=genai.protos.Type.OBJECT, properties={})
            )
            
            clear_declaration = genai.protos.FunctionDeclaration(
                name="clear_requirements",
                description="Xóa tất cả requirements đã lưu",
                parameters=genai.protos.Schema(type=genai.protos.Type.OBJECT, properties={})
            )
            
            tools = genai.protos.Tool(function_declarations=[
                ingest_raw_declaration,
                analyze_declaration,
                identify_declaration,
                prioritize_declaration,
                validate_req_declaration,
                generate_report_declaration,
                store_context_declaration,
                search_context_declaration,
                help_declaration,
                clear_declaration
            ])
            
            system_instruction = f"""Bạn là Business Analysis Assistant - Chuyên gia phân tích nghiệp vụ và Use Case.

🎯 SCOPE NGHIÊM NGẶT - CHỈ hỗ trợ Business Analysis & Use Case Analysis:
✅ Business Requirements Analysis
✅ Use Case Modeling & Specifications  
✅ Context Diagram & Use Case Diagram
✅ Stakeholder Analysis
✅ Business Process Analysis
✅ Requirements Prioritization

❌ KHÔNG hỗ trợ: Coding, Database Design, Technical Implementation, Testing, Project Management, General Chat

📊 Context hiện tại:
- Đã lưu: {len(self.collected_requirements)} requirements
- Trạng thái: {self.pipeline_state}

🎯 Workflow tự động khi nhận Business Requirements/Use Cases:
1. ingest_raw_requirements → Thu thập và chuẩn hóa requirements
2. analyze_stories → Phân tích use cases, tìm actors, scenarios, issues
3. identify_requirements → Xác định core business requirements & use cases
4. prioritize_requirements → Ưu tiên theo business value (MoSCoW)
5. validate_requirements → Validate completeness và consistency
6. generate_context_diagram → Tạo Context Diagram + Use Case Diagram (Mermaid)
7. store_conversation_context → Lưu analysis vào DB với embeddings

⚠️ NẾU user hỏi NGOÀI SCOPE:
- Lịch sự từ chối: "Xin lỗi, tôi chỉ chuyên về Business Analysis và Use Case Analysis. Tôi không thể hỗ trợ [topic]. Bạn có thể đặt câu hỏi về phân tích nghiệp vụ hoặc use case không?"
- KHÔNG cố gắng trả lời câu hỏi về coding, technical, hoặc topics khác

💡 Phong cách giao tiếp:
- Thân thiện, nhiệt tình như một Business Analyst chuyên nghiệp
- Trả lời tự nhiên, sinh động, không cứng nhắc
- Chủ động đề xuất cải thiện requirements nếu phát hiện thiếu sót
- Giải thích insights từ analysis một cách dễ hiểu
- Khen ngợi khi requirements được viết rõ ràng

📝 Input formats được hỗ trợ:
- Business Requirements: "The business needs to [objective] in order to [benefit]"
- User Stories: "As a [actor], I want to [action] so that [benefit]"
- Use Cases: "Actor: [who], Goal: [what], Scenario: [steps]"
- Functional Requirements: "The system shall/must [capability]"
- Business Rules: "When [condition] then [action]"
- Business Process: Mô tả quy trình nghiệp vụ hiện tại hoặc mong muốn
- Stakeholder Needs: Nhu cầu của các bên liên quan

🔧 MCP Tools Available (chỉ dùng cho Business Analysis):
- ingest_raw_requirements: Thu thập business requirements và use cases
- analyze_stories: Phân tích use cases, identify actors, scenarios, gaps
- identify_requirements: Extract core business requirements và use cases
- prioritize_requirements: Ưu tiên theo business value (MoSCoW method)
- validate_requirements: Validate completeness, consistency, testability
- generate_context_diagram: Tạo Context Diagram + Use Case Diagram (Mermaid)
- store_conversation_context: Lưu business analysis vào DB với embeddings
- search_previous_context: Tìm previous business analysis
- show_help, clear_requirements: Utilities

⚡ Hành động thông minh:
- Tự động gọi ingest_raw_requirements khi nhận raw text từ user
- Chain các MCP tools để tạo complete analysis pipeline
- Tự động store summary + embeddings vào DB conversation sau khi hoàn thành
- Search trong user's conversations bằng semantic similarity (embeddings)
- Load existing context khi reconnect to conversation
- Present kết quả với insights và recommendations"""
            
            model = genai.GenerativeModel(
                MODEL,
                system_instruction=system_instruction,
                tools=[tools],
                generation_config={
                    "temperature": 0.8,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 2048,
                }
            )
            
            # Build conversation history
            history = []
            for msg in self.conversation_history[-8:]:
                role = "user" if msg["role"] == "user" else "model"
                history.append({"role": role, "parts": [msg["content"]]})
            
            chat = model.start_chat(history=history)
            response = await asyncio.to_thread(chat.send_message, message)
            
            # Handle function calls (may chain multiple tools)
            max_iterations = 10  # Prevent infinite loops
            iteration = 0
            
            while iteration < max_iterations:
                iteration += 1
                
                if not (response.candidates and response.candidates[0].content.parts):
                    break
                
                function_calls = []
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        function_calls.append(part.function_call)
                
                if not function_calls:
                    break
                
                # Execute all function calls
                function_responses = []
                for fc in function_calls:
                    tool_result = await self._execute_tool(fc.name, dict(fc.args))
                    function_responses.append(
                        genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=fc.name,
                                response=tool_result
                            )
                        )
                    )
                
                # Send all results back to Gemini
                response = await asyncio.to_thread(
                    chat.send_message,
                    genai.protos.Content(parts=function_responses)
                )
                
                # If Gemini has final text response, break
                if hasattr(response, 'text') and response.text:
                    break
            
            # Auto-collect requirements if detected (and not already processed by tools)
            if self._is_requirement(message) and message not in self.collected_requirements:
                self.collected_requirements.append(message)
                count = len(self.collected_requirements)
                base_response = response.text if hasattr(response, 'text') else str(response)
                return f"{base_response}\n\n✅ Đã tự động lưu requirement #{count}."
            
            if hasattr(response, 'text'):
                return response.text
            return str(response)
            
        except Exception as e:
            return f"❌ Lỗi: {str(e)}"
    
    async def _execute_tool(self, tool_name: str, args: dict) -> dict:
        """Execute MCP tool based on Gemini's function call."""
        try:
            from api.services import mcp_adapter
            
            if tool_name == "ingest_raw_requirements":
                items = args.get("items", [])
                if not items:
                    return {"error": "No items provided"}
                
                # Save to collected requirements
                self.collected_requirements.extend(items)
                
                # Call MCP Collector: ingest_raw
                result = await asyncio.to_thread(
                    mcp_adapter.call_mcp,
                    "mcp_collector",
                    "ingest_raw",
                    {"items": items}
                )
                
                if result.get("error"):
                    return {"error": result.get("error")}
                
                chunks = result.get("response", {}).get("chunks", [])
                
                # Call MCP Collector: extract_stories
                stories_result = await asyncio.to_thread(
                    mcp_adapter.call_mcp,
                    "mcp_collector",
                    "extract_stories",
                    {"chunks": chunks}
                )
                
                if stories_result.get("error"):
                    return {"error": stories_result.get("error")}
                
                stories = stories_result.get("response", {}).get("stories", [])
                
                # Cache for summary
                self.last_pipeline_result["stories"] = stories
                
                return {
                    "success": True,
                    "message": f"✅ Thu thập {len(items)} requirements → {len(stories)} stories",
                    "stories": stories,
                    "chunks": chunks
                }
            
            elif tool_name == "analyze_stories":
                stories = args.get("stories", [])
                if not stories:
                    return {"error": "No stories to analyze"}
                
                # Call MCP Analyzer
                result = await asyncio.to_thread(
                    mcp_adapter.call_mcp,
                    "mcp_analyzer",
                    "analyze_stories",
                    {"stories": stories, "options": {"use_llm": True}}
                )
                
                if result.get("error"):
                    return {"error": result.get("error")}
                
                analysis = result.get("response", {}).get("analysis", {})
                enriched_stories = result.get("response", {}).get("stories", stories)
                
                # Cache for summary
                self.last_pipeline_result["analysis"] = analysis
                self.last_pipeline_result["stories"] = enriched_stories
                
                return {
                    "success": True,
                    "message": f"📊 Phân tích: {analysis.get('summary', {}).get('total_issues', 0)} issues found",
                    "stories": enriched_stories,
                    "analysis": analysis
                }
            
            elif tool_name == "identify_requirements":
                stories = args.get("stories", [])
                if not stories:
                    return {"error": "No stories provided"}
                
                # Call MCP Requirement: identify
                result = await asyncio.to_thread(
                    mcp_adapter.call_mcp,
                    "mcp_requirement",
                    "identify_requirements",
                    {"stories": stories, "options": {"use_llm": True}}
                )
                
                if result.get("error"):
                    return {"error": result.get("error")}
                
                requirements = result.get("response", {}).get("requirements", [])
                
                # Cache for summary
                self.last_pipeline_result["requirements"] = requirements
                
                return {
                    "success": True,
                    "message": f"🎯 Xác định {len(requirements)} core requirements",
                    "requirements": requirements
                }
            
            elif tool_name == "prioritize_requirements":
                requirements = args.get("requirements", [])
                if not requirements:
                    return {"error": "No requirements to prioritize"}
                
                # Call MCP Requirement: prioritize
                result = await asyncio.to_thread(
                    mcp_adapter.call_mcp,
                    "mcp_requirement",
                    "prioritize",
                    {"requirements": requirements}
                )
                
                if result.get("error"):
                    return {"error": result.get("error")}
                
                prioritized = result.get("response", {}).get("requirements", [])
                
                return {
                    "success": True,
                    "message": f"⭐ Đã ưu tiên {len(prioritized)} requirements",
                    "requirements": prioritized
                }
            
            elif tool_name == "validate_requirements":
                requirements = args.get("requirements", [])
                if not requirements:
                    return {"error": "No requirements to validate"}
                
                # Call MCP Validator
                result = await asyncio.to_thread(
                    mcp_adapter.call_mcp,
                    "mcp_validator",
                    "validate_requirements",
                    {"requirements": requirements}
                )
                
                if result.get("error"):
                    return {"error": result.get("error")}
                
                issues = result.get("response", {}).get("issues", [])
                
                # Cache for summary
                self.last_pipeline_result["validation_issues"] = issues
                
                return {
                    "success": True,
                    "message": f"✓ Validation: {len(issues)} issues found" if issues else "✓ All requirements valid",
                    "issues": issues,
                    "requirements": requirements  # Pass through for next step
                }
            
            elif tool_name == "generate_context_diagram":
                requirements = args.get("requirements", [])
                if not requirements:
                    return {"error": "No requirements for diagram"}
                
                # Call MCP Reporter
                result = await asyncio.to_thread(
                    mcp_adapter.call_mcp,
                    "mcp_reporter",
                    "generate_report",
                    {"requirements": requirements}
                )
                
                if result.get("error"):
                    return {"error": result.get("error")}
                
                report = result.get("response", {}).get("report", {})
                diagram = report.get("context_diagram", "")
                
                # Cache for summary
                self.last_pipeline_result["diagram"] = diagram
                self.last_pipeline_result["report"] = report
                
                return {
                    "success": True,
                    "message": "🎨 Context diagram created",
                    "diagram": diagram,
                    "report": report,
                    "requirements": requirements  # Pass through for storage
                }
            
            elif tool_name == "store_conversation_context":
                summary = args.get("summary", "")
                requirements = args.get("requirements", self.last_pipeline_result.get("requirements", []))
                diagram = args.get("diagram", self.last_pipeline_result.get("diagram", ""))
                
                # Auto-generate summary if not provided
                if not summary:
                    analysis = self.last_pipeline_result.get("analysis", {})
                    validation_issues = self.last_pipeline_result.get("validation_issues", [])
                    stories = self.last_pipeline_result.get("stories", [])
                    
                    summary = f"""Requirements Analysis Session
                    
User provided {len(self.collected_requirements)} requirements
Extracted {len(stories)} user stories
Identified {len(requirements)} core requirements
Analysis found {analysis.get('summary', {}).get('total_issues', 0)} issues
Validation found {len(validation_issues)} completeness issues

Key Requirements:
{chr(10).join([f"- {r.get('title', 'Untitled')}" for r in requirements[:5]])}
"""
                
                # Prepare full context document for embedding
                context_text = f"""Summary: {summary}

Requirements Count: {len(requirements)}

Requirements:
{json.dumps(requirements, indent=2, ensure_ascii=False)}

Analysis:
{json.dumps(self.last_pipeline_result.get("analysis", {}), indent=2, ensure_ascii=False)}

Validation Issues:
{json.dumps(self.last_pipeline_result.get("validation_issues", []), indent=2, ensure_ascii=False)}

Context Diagram:
{diagram}
"""
                
                # Generate embedding for semantic search
                embedding = await self._generate_embedding(context_text)
                
                # Save to conversation DB (primary storage)
                await self._save_conversation_summary(context_text, embedding)
                
                # Also store in vector MCP for additional search capabilities
                try:
                    context_id = f"conv_{self.conversation_id}_{int(datetime.utcnow().timestamp())}"
                    await asyncio.to_thread(
                        mcp_adapter.call_mcp,
                        "mcp_vector",
                        "ingest",
                        {
                            "ids": [context_id],
                            "texts": [context_text],
                            "metadatas": [{
                                "conversation_id": self.conversation_id,
                                "user_id": self.user_id,
                                "timestamp": datetime.utcnow().isoformat(),
                                "requirements_count": len(requirements),
                                "type": "requirements_analysis"
                            }]
                        }
                    )
                except Exception as e:
                    print(f"Warning: Vector MCP storage failed: {e}")
                
                return {
                    "success": True,
                    "message": "💾 Context saved to DB with embeddings",
                    "summary_length": len(context_text),
                    "embedding_dim": len(embedding) if embedding else 0
                }
            
            elif tool_name == "search_previous_context":
                query = args.get("query", "")
                top_k = args.get("top_k", 5)
                
                if not query:
                    return {"error": "No query provided"}
                
                # Generate query embedding
                query_embedding = await self._generate_embedding(query)
                
                # Search in conversation DB using embeddings
                formatted_results = []
                
                try:
                    async with async_session() as db:
                        from sqlalchemy import select, func
                        from api.core.models import Conversation
                        
                        # Get all conversations with embeddings for this user
                        stmt = select(Conversation).where(
                            Conversation.user_id == self.user_id,
                            Conversation.summary_embedding.isnot(None),
                            Conversation.status == 1
                        )
                        result = await db.execute(stmt)
                        conversations = result.scalars().all()
                        
                        # Calculate cosine similarity with query
                        similarities = []
                        for conv in conversations:
                            if conv.summary_embedding and query_embedding:
                                # Cosine similarity
                                import numpy as np
                                conv_emb = np.array(conv.summary_embedding)
                                query_emb = np.array(query_embedding)
                                
                                # Normalize
                                conv_norm = conv_emb / np.linalg.norm(conv_emb)
                                query_norm = query_emb / np.linalg.norm(query_emb)
                                
                                similarity = np.dot(conv_norm, query_norm)
                                similarities.append((conv, similarity))
                        
                        # Sort by similarity and take top_k
                        similarities.sort(key=lambda x: x[1], reverse=True)
                        top_results = similarities[:top_k]
                        
                        # Format results
                        for i, (conv, sim) in enumerate(top_results, 1):
                            summary_preview = conv.summary[:500] + "..." if conv.summary and len(conv.summary) > 500 else conv.summary
                            formatted_results.append({
                                "rank": i,
                                "conversation_id": conv.id,
                                "conversation_name": conv.name,
                                "content": summary_preview,
                                "created_at": conv.created_at.isoformat() if conv.created_at else None,
                                "similarity": float(sim)
                            })
                
                except Exception as e:
                    # Fallback to vector MCP search
                    print(f"DB search failed, using vector MCP: {e}")
                    try:
                        result = await asyncio.to_thread(
                            mcp_adapter.call_mcp,
                            "mcp_vector",
                            "search",
                            {"query": query, "top_k": top_k}
                        )
                        
                        if not result.get("error"):
                            search_result = result.get("response", {}).get("result", {})
                            documents = search_result.get("documents", [[]])[0]
                            metadatas = search_result.get("metadatas", [[]])[0]
                            distances = search_result.get("distances", [[]])[0]
                            
                            for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances)):
                                formatted_results.append({
                                    "rank": i + 1,
                                    "content": doc[:500] + "..." if len(doc) > 500 else doc,
                                    "metadata": meta,
                                    "similarity": 1 - dist
                                })
                    except Exception as e2:
                        print(f"Vector MCP search also failed: {e2}")
                
                return {
                    "success": True,
                    "message": f"🔍 Found {len(formatted_results)} previous contexts from DB",
                    "results": formatted_results
                }
            
            elif tool_name == "show_help":
                return {"success": True, "message": self._get_help()}
            
            elif tool_name == "clear_requirements":
                self.collected_requirements.clear()
                self.pipeline_state = "idle"
                return {"success": True, "message": "✅ Đã xóa tất cả requirements"}
            
            return {"error": f"Unknown tool: {tool_name}"}
            
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}", "trace": traceback.format_exc()}

    def _get_help(self) -> str:
        """Return help text."""
        return """🎯 Business Analysis & Use Case Assistant

📋 SCOPE - Chỉ hỗ trợ:
✅ Business Requirements Analysis
✅ Use Case Analysis & Modeling
✅ Context Diagram & Use Case Diagram
✅ Stakeholder Analysis
✅ Business Process Analysis

❌ KHÔNG hỗ trợ: Coding, Database, Technical Implementation, Testing

📝 Input Formats:
• Business Requirement: "The business needs to [objective]"
• User Story: "As a [actor], I want to [action] so that [benefit]"
• Use Case: "Actor: [who], Goal: [what], Main Flow: [steps]"
• Business Process: Mô tả quy trình nghiệp vụ
• Stakeholder Need: Nhu cầu của các bên liên quan

🔄 Workflow:
1. Thu thập requirements/use cases
2. Phân tích nghiệp vụ, identify actors, scenarios
3. Tìm gaps, conflicts, ambiguity
4. Ưu tiên theo business value (MoSCoW)
5. Tạo Context Diagram + Use Case Diagram
6. Generate Use Case Specifications

💡 Example:
"Phân tích use case đăng nhập cho hệ thống"
"Tôi cần context diagram cho ứng dụng quản lý bán hàng"
"Phân tích business requirements cho tính năng thanh toán"

� Search Previous:
"Tìm analysis về authentication use case"
"Show me previous payment requirements"

💾 Tất cả analysis được lưu tự động với embeddings để recall sau."""
