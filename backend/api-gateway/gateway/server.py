"""FastAPI WebSocket server for AI agent chat bot.

This server provides:
- WebSocket endpoint for real-time bi-directional communication
- Session management for multiple concurrent users
- Agent-based message handling
- Broadcasting capabilities
- Health check endpoints
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid
import logging
from typing import Optional

from gateway.agents.chat_agent import ChatAgent
from gateway.utils.session import SessionManager
from gateway.utils.message import Message, MessageType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Agent WebSocket Gateway",
    description="WebSocket server for real-time AI agent communication",
    version="1.0.0"
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize session manager
session_manager = SessionManager()


@app.get("/")
async def root():
    """Root endpoint with basic info and WebSocket test client."""
    html_content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>AI Agent WebSocket</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 50px auto;
                    padding: 20px;
                    background: #f5f5f5;
                }
                .container {
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                h1 {
                    color: #333;
                }
                .chat-box {
                    border: 1px solid #ddd;
                    padding: 15px;
                    height: 300px;
                    overflow-y: auto;
                    background: #fafafa;
                    margin: 20px 0;
                    border-radius: 4px;
                }
                .message {
                    margin: 5px 0;
                    padding: 8px;
                    border-radius: 4px;
                }
                .user-message {
                    background: #e3f2fd;
                    text-align: right;
                }
                .agent-message {
                    background: #f1f8e9;
                }
                .system-message {
                    background: #fff3e0;
                    font-style: italic;
                    color: #666;
                }
                .input-group {
                    display: flex;
                    gap: 10px;
                }
                input {
                    flex: 1;
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    font-size: 14px;
                }
                button {
                    padding: 10px 20px;
                    background: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 14px;
                }
                button:hover {
                    background: #45a049;
                }
                button:disabled {
                    background: #ccc;
                    cursor: not-allowed;
                }
                .status {
                    padding: 10px;
                    margin: 10px 0;
                    border-radius: 4px;
                    font-weight: bold;
                }
                .connected {
                    background: #c8e6c9;
                    color: #2e7d32;
                }
                .disconnected {
                    background: #ffcdd2;
                    color: #c62828;
                }
                code {
                    background: #f5f5f5;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-family: monospace;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 AI Agent WebSocket Test</h1>
                <div id="status" class="status disconnected">Disconnected</div>
                
                <div class="chat-box" id="chatBox"></div>
                
                <div class="input-group">
                    <input 
                        type="text" 
                        id="messageInput" 
                        placeholder="Type your message... (try 'ping', '/help', or any text)"
                        disabled
                    />
                    <button id="sendBtn" disabled>Send</button>
                    <button id="connectBtn">Connect</button>
                </div>
                
                <div style="margin-top: 20px; color: #666; font-size: 14px;">
                    <p><strong>API Endpoints:</strong></p>
                    <ul>
                        <li>WebSocket: <code>ws://localhost:8000/ws/chat</code></li>
                        <li>Health: <code>GET /health</code></li>
                        <li>Stats: <code>GET /stats</code></li>
                    </ul>
                </div>
            </div>

            <script>
                let ws = null;
                const chatBox = document.getElementById('chatBox');
                const messageInput = document.getElementById('messageInput');
                const sendBtn = document.getElementById('sendBtn');
                const connectBtn = document.getElementById('connectBtn');
                const status = document.getElementById('status');

                function addMessage(content, type) {
                    const msg = document.createElement('div');
                    msg.className = `message ${type}-message`;
                    msg.textContent = content;
                    chatBox.appendChild(msg);
                    chatBox.scrollTop = chatBox.scrollHeight;
                }

                function setConnected(connected) {
                    if (connected) {
                        status.textContent = 'Connected ✓';
                        status.className = 'status connected';
                        messageInput.disabled = false;
                        sendBtn.disabled = false;
                        connectBtn.textContent = 'Disconnect';
                    } else {
                        status.textContent = 'Disconnected ✗';
                        status.className = 'status disconnected';
                        messageInput.disabled = true;
                        sendBtn.disabled = true;
                        connectBtn.textContent = 'Connect';
                    }
                }

                function connect() {
                    if (ws && ws.readyState === WebSocket.OPEN) {
                        ws.close();
                        return;
                    }

                    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                    const wsUrl = `${protocol}//${window.location.host}/ws/chat`;
                    
                    ws = new WebSocket(wsUrl);

                    ws.onopen = () => {
                        setConnected(true);
                        addMessage('Connected to agent server', 'system');
                    };

                    ws.onmessage = (event) => {
                        try {
                            const data = JSON.parse(event.data);
                            if (data.type === 'error') {
                                addMessage(`Error: ${data.content}`, 'system');
                            } else if (data.type === 'system') {
                                addMessage(data.content, 'system');
                            } else {
                                addMessage(data.content, 'agent');
                            }
                        } catch {
                            addMessage(event.data, 'agent');
                        }
                    };

                    ws.onerror = (error) => {
                        addMessage('Connection error', 'system');
                        console.error('WebSocket error:', error);
                    };

                    ws.onclose = () => {
                        setConnected(false);
                        addMessage('Disconnected from server', 'system');
                    };
                }

                function sendMessage() {
                    const message = messageInput.value.trim();
                    if (!message || !ws || ws.readyState !== WebSocket.OPEN) return;

                    addMessage(message, 'user');
                    ws.send(message);
                    messageInput.value = '';
                }

                connectBtn.onclick = connect;
                sendBtn.onclick = sendMessage;
                messageInput.onkeypress = (e) => {
                    if (e.key === 'Enter') sendMessage();
                };
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse({
        "status": "healthy",
        "service": "ai-agent-gateway",
        "active_sessions": session_manager.get_active_count()
    })


@app.get("/stats")
async def get_stats():
    """Get server statistics."""
    return JSONResponse({
        "active_sessions": session_manager.get_active_count(),
        "total_connections": session_manager.get_active_count(),  # Could track historical data
    })


@app.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    """WebSocket endpoint for chat communication.
    
    Each connection creates a new session with its own agent instance.
    Messages are processed by the agent and responses are pushed back to the client.
    """
    session_id = str(uuid.uuid4())
    agent = None
    
    try:
        # Accept WebSocket connection
        await websocket.accept()
        logger.info(f"New WebSocket connection: {session_id}")
        
        # Create agent instance for this session
        agent = ChatAgent(session_id)
        
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


@app.post("/broadcast")
async def broadcast_message(message: str, api_key: Optional[str] = None):
    """Broadcast a message to all active sessions.
    
    This endpoint allows server-side components to push messages to all connected clients.
    In production, this should be protected with proper authentication.
    
    Args:
        message: Message to broadcast
        api_key: Optional API key for authentication
    """
    # In production, validate api_key here
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")
    
    broadcast_msg = Message.system(message)
    await session_manager.broadcast(broadcast_msg.to_json())
    
    return JSONResponse({
        "status": "success",
        "message": "Broadcast sent",
        "recipients": session_manager.get_active_count()
    })


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Log server startup."""
    logger.info("AI Agent WebSocket Gateway started")
    logger.info("WebSocket endpoint: ws://localhost:8000/ws/chat")


@app.on_event("shutdown")
async def shutdown_event():
    """Log server shutdown."""
    logger.info("AI Agent WebSocket Gateway shutting down")
