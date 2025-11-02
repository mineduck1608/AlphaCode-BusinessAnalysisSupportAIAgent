# AI Agent WebSocket Gateway

WebSocket server cho AI agent chat bot với khả năng push tin nhắn real-time lên UI.

## 🏗️ Cấu trúc thư mục

```
api-gateway/
├── main.py                    # Entry point chính
├── requirements.txt           # Dependencies
├── README.md                  # File này
└── gateway/                   # Package chính
    ├── __init__.py
    ├── server.py             # FastAPI WebSocket server
    ├── agents/               # Các AI agent implementations
    │   ├── __init__.py
    │   ├── base_agent.py    # Base class cho agents
    │   └── chat_agent.py    # Chat agent implementation
    └── utils/                # Utilities
        ├── __init__.py
        ├── session.py       # Session management
        └── message.py       # Message formatting
```

## 🚀 Cách chạy server

### 1. Cài đặt dependencies

```powershell
cd d:\Code\Hackathon\AlphaCode\backend\api-gateway
pip install -r requirements.txt
```

### 2. Chạy server

**Cách 1: Chạy trực tiếp với Python**
```powershell
python main.py
```

**Cách 2: Chạy với Uvicorn (production)**
```powershell
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Server sẽ chạy tại: `http://localhost:8000`

## 📡 API Endpoints

### WebSocket Endpoint
- **URL**: `ws://localhost:8000/ws/chat`
- **Protocol**: WebSocket
- **Usage**: Kết nối để chat real-time với AI agent

### HTTP Endpoints
- **GET** `/` - Test page với WebSocket client demo
- **GET** `/health` - Health check
- **GET** `/stats` - Server statistics
- **POST** `/broadcast` - Broadcast message to all connected clients

## 💬 Cách test WebSocket

### Test trong trình duyệt
1. Mở: `http://localhost:8000`
2. Click nút "Connect"
3. Gõ tin nhắn và gửi

### Test với JavaScript

```javascript
// Kết nối WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/chat');

ws.onopen = () => {
    console.log('Connected!');
    // Gửi tin nhắn
    ws.send('Hello from client');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};

ws.onerror = (error) => {
    console.error('Error:', error);
};

ws.onclose = () => {
    console.log('Disconnected');
};
```

### Test với Python client

```python
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/chat"
    
    async with websockets.connect(uri) as websocket:
        # Gửi tin nhắn
        await websocket.send("Hello from Python")
        
        # Nhận response
        response = await websocket.recv()
        data = json.loads(response)
        print(f"Received: {data}")

asyncio.run(test_websocket())
```

## 🔧 Message Format

Server hỗ trợ 2 loại message format:

### 1. Plain text (simple)
```
"Hello, how are you?"
```

### 2. JSON format (structured)
```json
{
  "type": "text",
  "content": "Hello, how are you?",
  "metadata": {},
  "timestamp": "2025-11-02T10:30:00"
}
```

## 📝 Available Commands

Gõ các command này trong chat:
- `ping` - Test connection
- `/help` - Show help
- `/history` - Show conversation history
- `/clear` - Clear conversation history
- `/whoami` - Show session info

## 🔌 Tích hợp với Frontend (React/Next.js)

### Hook để sử dụng WebSocket

```typescript
// useWebSocket.ts
import { useEffect, useRef, useState } from 'react';

export function useWebSocket(url: string) {
  const [messages, setMessages] = useState<any[]>([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages(prev => [...prev, data]);
    };

    ws.onclose = () => {
      setConnected(false);
      console.log('WebSocket disconnected');
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return () => {
      ws.close();
    };
  }, [url]);

  const sendMessage = (message: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(message);
    }
  };

  return { messages, connected, sendMessage };
}
```

### Component sử dụng

```tsx
// ChatComponent.tsx
import { useWebSocket } from './useWebSocket';

export function ChatComponent() {
  const { messages, connected, sendMessage } = useWebSocket('ws://localhost:8000/ws/chat');
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim()) {
      sendMessage(input);
      setInput('');
    }
  };

  return (
    <div>
      <div>Status: {connected ? '✅ Connected' : '❌ Disconnected'}</div>
      
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx}>{msg.content}</div>
        ))}
      </div>
      
      <input 
        value={input} 
        onChange={e => setInput(e.target.value)}
        onKeyPress={e => e.key === 'Enter' && handleSend()}
      />
      <button onClick={handleSend}>Send</button>
    </div>
  );
}
```

## 🎯 Features

✅ **Real-time WebSocket communication**
- Bi-directional messaging
- Automatic reconnection handling
- Session management

✅ **Agent-based architecture**
- Extensible agent system
- Conversation history tracking
- Command support

✅ **Broadcasting**
- Push messages to all connected clients
- Server-initiated notifications

✅ **Production-ready**
- CORS support
- Error handling
- Logging
- Health checks

## 🔐 Security Notes

Để production:
1. Thêm authentication cho WebSocket connections
2. Validate và sanitize user input
3. Rate limiting
4. Bảo vệ `/broadcast` endpoint với API key
5. Sử dụng WSS (WebSocket Secure) với HTTPS

## 📊 Monitoring

Kiểm tra số lượng connections:
```powershell
curl http://localhost:8000/stats
```

Response:
```json
{
  "active_sessions": 5,
  "total_connections": 5
}
```

## 🐛 Troubleshooting

**Lỗi: Module not found**
```powershell
# Đảm bảo đang ở đúng thư mục
cd d:\Code\Hackathon\AlphaCode\backend\api-gateway
# Cài lại dependencies
pip install -r requirements.txt
```

**Lỗi: Port already in use**
```powershell
# Đổi port trong main.py hoặc dùng uvicorn với port khác
uvicorn main:app --port 8001
```

**WebSocket connection failed**
- Kiểm tra server đang chạy
- Kiểm tra URL đúng (`ws://` không phải `http://`)
- Kiểm tra firewall settings

## 📚 Next Steps

1. Tích hợp LLM (OpenAI, Anthropic, etc.) vào `ChatAgent`
2. Thêm database để lưu conversation history
3. Implement streaming responses
4. Thêm file upload support
5. Multi-agent support với routing
