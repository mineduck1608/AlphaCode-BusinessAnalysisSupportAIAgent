# WebSocket Chat Integration

Phần WebSocket đã được tích hợp vào API backend để hỗ trợ real-time chat communication.

## Endpoints

### WebSocket Endpoint
- **URL**: `ws://localhost:8000/ws/chat`
- **Protocol**: WebSocket
- **Description**: Endpoint cho real-time bi-directional communication với AI chat agent

### HTTP Endpoints
- **GET** `/health` - Health check (bao gồm số lượng active WebSocket sessions)
- **GET** `/ws/stats` - Thống kê WebSocket sessions

## Message Format

### Gửi tin nhắn từ client
Có thể gửi plain text hoặc JSON format:

**Plain Text:**
```
Hello, how are you?
```

**JSON Format:**
```json
{
  "type": "text",
  "content": "Hello, how are you?",
  "metadata": {}
}
```

### Nhận tin nhắn từ server
Server luôn trả về JSON format:

```json
{
  "type": "text",
  "content": "Response message here",
  "metadata": {},
  "timestamp": "2025-11-02T10:30:00.123456"
}
```

### Message Types
- `text` - Tin nhắn thông thường
- `system` - Tin nhắn hệ thống
- `error` - Thông báo lỗi
- `typing` - Typing indicator

## Special Commands

Agent hỗ trợ các lệnh đặc biệt:

- `/help` - Hiển thị help message
- `/history` - Xem conversation history
- `/clear` - Xóa conversation history
- `/whoami` - Thông tin session
- `ping` - Test connection (trả về "pong")

## Cách sử dụng

### JavaScript/TypeScript Client

```javascript
// Kết nối WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/chat');

// Xử lý khi kết nối thành công
ws.onopen = () => {
  console.log('Connected to chat server');
};

// Nhận tin nhắn từ server
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message.content);
};

// Gửi tin nhắn
function sendMessage(text) {
  ws.send(text);
  // hoặc gửi JSON:
  // ws.send(JSON.stringify({ type: 'text', content: text }));
}

// Xử lý lỗi
ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

// Xử lý khi ngắt kết nối
ws.onclose = () => {
  console.log('Disconnected from server');
};
```

### Python Client

```python
import asyncio
import websockets
import json

async def chat():
    uri = "ws://localhost:8000/ws/chat"
    async with websockets.connect(uri) as websocket:
        # Nhận welcome message
        welcome = await websocket.recv()
        print(f"Server: {json.loads(welcome)['content']}")
        
        # Gửi tin nhắn
        await websocket.send("Hello, AI!")
        
        # Nhận response
        response = await websocket.recv()
        message = json.loads(response)
        print(f"Agent: {message['content']}")

asyncio.run(chat())
```

## Architecture

```
api/
├── main.py                    # FastAPI app với WebSocket endpoint
├── websocket/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py     # Base class cho các agents
│   │   └── chat_agent.py     # Chat agent implementation
│   └── utils/
│       ├── __init__.py
│       ├── message.py         # Message formatting utilities
│       └── session.py         # Session management
```

## Session Management

- Mỗi WebSocket connection tạo một session riêng với unique session ID
- SessionManager track tất cả active connections
- Mỗi session có agent instance riêng để maintain conversation context
- Auto cleanup khi connection đóng

## Testing

Để test WebSocket endpoint:

1. Start server:
```bash
cd backend
uvicorn api.main:app --reload
```

2. Sử dụng công cụ test WebSocket như:
   - Browser console với WebSocket API
   - Postman (hỗ trợ WebSocket)
   - wscat: `npm install -g wscat && wscat -c ws://localhost:8000/ws/chat`
   - Python websockets client

## Notes

- WebSocket endpoint này thay thế cho api-gateway cũ
- UI code không được migrate (theo yêu cầu)
- Agent hiện tại là demo implementation, có thể mở rộng để tích hợp với AI models thật
- CORS đã được cấu hình để cho phép tất cả origins (nên giới hạn trong production)
