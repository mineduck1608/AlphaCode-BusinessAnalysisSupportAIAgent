import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uuid
import logging

from api.routers import conversation
from api.routers import conversation_agent
from api.routers import agent
from api.routers import user
from api.routers import role
from api.routers import prompt
from api.routers import message
from api.routers import shared_conversation
from api.routers import mcp
from api.websocket.agents.chat_agent import ChatAgent
from api.websocket.utils.session import SessionManager
from api.websocket.utils.message import Message

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="AlphaCode API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize WebSocket session manager
session_manager = SessionManager()

# register routers
app.include_router(conversation.router, tags=["conversation"])
app.include_router(conversation_agent.router, tags=["conversation-agent"])
app.include_router(agent.router, tags=["agent"])
app.include_router(user.router, tags=["user"])
app.include_router(role.router, tags=["role"])
app.include_router(prompt.router, tags=["prompt"])
app.include_router(message.router, tags=["message"])
app.include_router(shared_conversation.router, tags=["shared-conversation"])
app.include_router(mcp.router, tags=["mcp"])

@app.get("/health")
def healthcheck():
    return {
        "status": "ok",
        "active_ws_sessions": session_manager.get_active_count()
    }

@app.get("/ws/stats")
async def get_ws_stats():
    """Get WebSocket server statistics."""
    return JSONResponse({
        "active_sessions": session_manager.get_active_count(),
    })

@app.get("/ws/conversation/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: int):
    """Get all messages from a conversation."""
    from api.core.db import async_session
    from api.core.models import Message
    from sqlalchemy import select
    
    async with async_session() as db:
        stmt = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc())
        result = await db.execute(stmt)
        messages = result.scalars().all()
        
        return [{
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "user_id": msg.user_id,
            "agent_id": msg.agent_id,
            "created_at": msg.created_at.isoformat() if msg.created_at else None
        } for msg in messages]

@app.websocket("/ws/chat")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    user_id: int = 1,  # Default user ID, should be from auth token
    agent_id: int = 1,  # Default agent ID
    conversation_id: int = None  # Optional: continue existing conversation
):
    """WebSocket endpoint for chat communication.
    
    Each connection creates a new session with its own agent instance.
    Messages are processed by the agent and responses are pushed back to the client.
    
    Query parameters:
    - user_id: User ID (default: 1)
    - agent_id: Agent ID (default: 1)
    - conversation_id: Optional conversation ID to continue existing chat
    """
    session_id = str(uuid.uuid4())
    agent = None
    
    try:
        # Accept WebSocket connection
        await websocket.accept()
        logger.info(f"New WebSocket connection: {session_id} (user={user_id}, agent={agent_id})")
        
        # Create agent instance for this session
        agent = ChatAgent(session_id, user_id=user_id, agent_id=agent_id)
        
        # Set conversation ID if continuing existing chat
        if conversation_id:
            agent.conversation_id = conversation_id
        
        # Register session
        session_manager.register(session_id, websocket, agent)
        
        # Send welcome message
        welcome_msg = Message.system(
            f"Welcome! Your session ID is {session_id[:8]}... Type /help for commands."
        )
        await websocket.send_text(welcome_msg.to_json())
        
        # Main message loop
        while True:
            # Receive message from client
            raw_message = await websocket.receive_text()
            logger.info(f"[{session_id[:8]}] Received: {raw_message[:100]}")
            
            # Parse message
            message = Message.from_json(raw_message)
            
            # Handle empty messages
            if not message.content.strip():
                continue
            
            try:
                # Send typing indicator (optional)
                typing_msg = Message.typing(True)
                await websocket.send_text(typing_msg.to_json())
                
                # Process message with agent
                response_text = await agent.handle_message(message.content)
                
                # Send response
                response_msg = Message.text(response_text)
                await websocket.send_text(response_msg.to_json())
                
                logger.info(f"[{session_id[:8]}] Sent response: {response_text[:100]}")
                
            except Exception as e:
                logger.error(f"Error processing message for {session_id}: {e}", exc_info=True)
                error_msg = Message.error(
                    f"Failed to process message: {str(e)}",
                    error_code="PROCESSING_ERROR"
                )
                await websocket.send_text(error_msg.to_json())
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
    
    except Exception as e:
        logger.error(f"Unexpected error for session {session_id}: {e}", exc_info=True)
    
    finally:
        # Clean up session
        session_manager.unregister(session_id)
        logger.info(f"Session cleaned up: {session_id}")

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Log server startup."""
    logger.info("AlphaCode API with WebSocket support started")
    logger.info("WebSocket endpoint: ws://localhost:8000/ws/chat")

@app.on_event("shutdown")
async def shutdown_event():
    """Log server shutdown."""
    logger.info("AlphaCode API shutting down")
