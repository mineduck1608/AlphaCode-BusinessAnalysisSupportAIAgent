"""FastAPI entrypoint for AI Agent WebSocket Gateway.

This module starts the WebSocket server when run directly.
For production, use: uvicorn main:app --host 0.0.0.0 --port 8000
For development, run: python main.py
"""

from gateway.server import app


def main():
    """Run the development server."""
    import uvicorn
    
    print("🚀 Starting AI Agent WebSocket Gateway...")
    print("📡 WebSocket endpoint: ws://localhost:8000/ws/chat")
    print("🌐 Test page: http://localhost:8000")
    print("💚 Health check: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False
    )


if __name__ == "__main__":
    main()