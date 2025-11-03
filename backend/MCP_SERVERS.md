# MCP Servers Documentation

## Overview
The system uses MCP (Model Context Protocol) to separate processing logic into independent microservices that communicate via STDIO.

## Architecture

```
User Input → ChatAgent (Gemini Orchestrator) → MCP Servers
                                                    ↓
                                          Function Calling Routing
                                                    ↓
                                    ┌───────────────┴───────────────┐
                                    ↓                               ↓
                            MCP Collector                   MCP Analyzer
                                    ↓                               ↓
                            MCP Requirement                 MCP Reporter
                                    ↓                               ↓
                                Context Diagram Output
```

## MCP Servers

### 1. mcp_collector
**Path**: `services/mcp_collector/src/server.py`

**Capabilities**:
- `ingest_raw`: Collect raw requirements
- `normalize`: Standardize text
- `extract_stories`: Extract user stories from chunks

**Prompt**: `prompts/collector.yml`

**Example**:
```python
result = mcp_adapter.call_mcp(
    "mcp_collector",
    "ingest_raw",
    {"items": ["As a user, I want to login..."]}
)
```

### 2. mcp_analyzer
**Path**: `services/mcp_analyzer/src/server.py`

**Capabilities**:
- `analyze_requirement`: Analyze text chunks
- `analyze_stories`: Analyze stories, find issues/conflicts
- `suggest_improvements`: Suggest improvements

**Prompt**: `prompts/analyzer.yml`

**Features**:
- Detect ambiguity, incompleteness, conflicts
- Find implicit assumptions
- Identify non-testable statements
- LLM-powered suggestions

**Example**:
```python
result = mcp_adapter.call_mcp(
    "mcp_analyzer",
    "analyze_stories",
    {
        "stories": stories,
        "options": {"use_llm": True}
    }
)
```

### 3. mcp_requirement
**Path**: `services/mcp_requirement/src/server.py`

**Capabilities**:
- `identify_requirements`: Identify core business requirements
- `prioritize`: Prioritize requirements by score

**Prompt**: `prompts/requirement.yml`

**Scoring Logic**:
- Length-based scoring
- Keyword detection (critical, must, should, optional)
- Acceptance criteria presence
- Urgency markers

**Example**:
```python
result = mcp_adapter.call_mcp(
    "mcp_requirement",
    "identify_requirements",
    {"stories": stories, "options": {"use_llm": True}}
)
```

### 4. mcp_reporter
**Path**: `services/mcp_reporter/src/server.py`

**Capabilities**:
- `generate_report`: Create report and context diagram (Mermaid)

**Prompt**: `prompts/reporter.yml`

**Output**:
- Summary
- Context diagram (Mermaid format)
- Requirements categorization

**Example**:
```python
result = mcp_adapter.call_mcp(
    "mcp_reporter",
    "generate_report",
    {"requirements": prioritized_requirements}
)
```

### 5. mcp_validator
**Path**: `services/mcp_validator/src/server.py`

**Capabilities**:
- `validate_requirements`: Check requirements structure (id, title, priority)
- `validate_report`: Validate report completeness
- `llm_check`: LLM-based validation with custom instructions

**Features**:
- Structure validation (missing fields)
- Count consistency checks
- Optional LLM-powered validation

**Example**:
```python
result = mcp_adapter.call_mcp(
    "mcp_validator",
    "validate_requirements",
    {"requirements": prioritized_requirements}
)
```

**Status**: ✅ Integrated in orchestrator

### 6. mcp_vector
**Path**: `services/mcp_vector/src/server.py`

**Capabilities**:
- `ingest`: Store documents with embeddings
- `search`: Semantic search with top_k results

**Technology**:
- ChromaDB for vector storage
- Google Gemini `text-embedding-004` for embeddings
- Persistent storage support

**Use Cases**:
- Store conversation context after analysis
- Retrieve previous requirements analysis
- Enable contextual memory across sessions

**Example**:
```python
# Store context
result = mcp_adapter.call_mcp(
    "mcp_vector",
    "ingest",
    {
        "ids": ["conv_123"],
        "texts": ["Requirements: ..."],
        "metadatas": [{"timestamp": "2025-11-03", "type": "analysis"}]
    }
)

# Search context
result = mcp_adapter.call_mcp(
    "mcp_vector",
    "search",
    {"query": "user authentication requirements", "top_k": 5}
)
```

**Status**: ✅ Integrated in orchestrator

### 7. mcp_ticket
**Path**: `services/mcp_ticket/src/server.py`

**Purpose**: Ticket management integration (Jira, GitHub Issues, etc.)

**Status**: ⚠️ Empty file - Not implemented yet

## Gemini Orchestrator Flow

### Function Calling Sequence

1. **User Input** → Gemini identifies intent
2. **Function Call**: `ingest_raw_requirements`
   - Collector collects and extracts stories
   - Return: stories[]
3. **Auto Chain**: `analyze_stories`
   - Analyzer analyzes stories
   - Return: enriched stories with analysis
4. **Auto Chain**: `identify_requirements`
   - Requirement extracts core requirements
   - Return: requirements[]
5. **Auto Chain**: `prioritize_requirements`
   - Requirement prioritize
   - Return: ranked requirements[]
6. **Auto Chain**: `validate_requirements`
   - Validator checks completeness
   - Return: validation issues[]
7. **Auto Chain**: `generate_context_diagram`
   - Reporter creates Mermaid diagram
   - Return: diagram + report
8. **Final Call**: `store_conversation_context`
   - Vector store saves context
   - Return: context_id

**Alternative Flows**:
- **Search Previous**: `search_previous_context`
   - When user asks about old requirements
   - Vector search returns previous analysis

### Gemini System Instruction

```python
system_instruction = f"""
📊 Context: {len(self.collected_requirements)} requirements saved

🎯 Workflow:
1. ingest_raw_requirements → Standardize
2. analyze_stories → Find issues
3. identify_requirements → Extract core reqs
4. prioritize_requirements → Ranking
5. generate_context_diagram → Visualization

💡 Style: Friendly, proactive, intelligent routing
"""
```

## Integration with WebSocket

### ChatAgent Flow

```python
class ChatAgent:
    async def _generate_response(self, message: str) -> str:
        # Gemini orchestrator with function calling
        return await self._call_gemini_orchestrator(message)
    
    async def _execute_tool(self, tool_name: str, args: dict) -> dict:
        # Route to appropriate MCP server
        if tool_name == "ingest_raw_requirements":
            result = await mcp_adapter.call_mcp("mcp_collector", "ingest_raw", ...)
        elif tool_name == "analyze_stories":
            result = await mcp_adapter.call_mcp("mcp_analyzer", "analyze_stories", ...)
        # ... etc
```

## Testing

### Start MCP Servers Manually

```bash
# Collector
python services/mcp_collector/src/server.py

# Analyzer
python services/mcp_analyzer/src/server.py

# Requirement
python services/mcp_requirement/src/server.py

# Reporter
python services/mcp_reporter/src/server.py
```

### Test Pipeline

```bash
python services/test_pipeline.py
```

### WebSocket Test

```bash
# Start backend
python -m uvicorn api.main:app --reload

# Open test_websocket.html in browser
# Connect to: ws://localhost:8000/ws/chat?user_id=1&agent_id=1
# Send: "As a user, I want to export reports"
```

## Environment Variables

Required in `.env`:

```env
GENAI_API_KEY=your_google_api_key
LLM_MODEL=gemini-2.0-flash-exp
DB_URL=postgresql://user:pass@host:5432/db
```

## Prompts Configuration

All prompts are defined in `prompts/` directory:
- `collector.yml` - Collector agent prompts
- `analyzer.yml` - Analyzer agent prompts
- `requirement.yml` - Requirement agent prompts
- `reporter.yml` - Reporter agent prompts

Format: Jinja2 templates with YAML metadata

## Benefits of This Architecture

✅ **Separation of Concerns**: Each MCP server handles one responsibility
✅ **Scalability**: Can run MCP servers on different machines
✅ **Testability**: Each MCP server can be tested independently
✅ **Flexibility**: Easy to swap or add new MCP servers
✅ **Intelligent Routing**: Gemini decides when to call which MCP server
✅ **Natural Conversation**: Users don't need to know MCP internals

## Summary - Current Status

### ✅ Fully Integrated (7/8 MCP Servers)

1. **mcp_collector** - Collect and standardize requirements ✅
2. **mcp_analyzer** - Analyze quality, find issues ✅
3. **mcp_requirement** - Identify and prioritize requirements ✅
4. **mcp_reporter** - Create context diagram (Mermaid) ✅
5. **mcp_validator** - Validate completeness and structure ✅
6. **mcp_vector** - Store/search conversation context with embeddings ✅
7. **common** - Shared utilities ✅

### ⏳ Not Yet Implemented

8. **mcp_ticket** - Empty file, need to implement Jira/GitHub integration

## Complete Workflow with Vector Store

```
User: "As a user, I want to login with email"
  ↓
Gemini Orchestrator detects requirements
  ↓
┌─────────────────────────────────────┐
│ MCP Pipeline (Auto-chained)         │
├─────────────────────────────────────┤
│ 1. ingest_raw_requirements          │
│ 2. analyze_stories                  │
│ 3. identify_requirements            │
│ 4. prioritize_requirements          │
│ 5. validate_requirements            │
│ 6. generate_context_diagram         │
│ 7. store_conversation_context       │
└─────────────────────────────────────┘
  ↓
Response with:
  - Analysis insights
  - Context diagram
  - Validation results
  - Context stored in vector DB

Later:
User: "Show me the login requirements we discussed"
  ↓
Gemini calls: search_previous_context
  ↓
Vector search returns previous analysis
```

## Key Benefits

✅ **Complete Pipeline**: 7-step automated analysis
✅ **Context Memory**: Vector store for cross-session recall
✅ **Quality Assurance**: Validation step ensures completeness
✅ **Intelligent Routing**: Gemini orchestrator decides flow
✅ **Natural Conversation**: User doesn't need to know MCP internals
✅ **Scalable**: Each MCP server is independent, can scale separately

## Next Steps

1. ✅ Gemini orchestrator with function calling
2. ✅ All main MCP servers integrated (7/8)
3. ✅ Validation step (mcp_validator)
4. ✅ Vector search (mcp_vector) with embeddings
5. ⏳ Implement mcp_ticket for Jira/GitHub integration
6. ⏳ Add prompt caching for better performance
7. ⏳ Add streaming responses for real-time feedback
