"""Run script for API server with WebSocket support."""
import sys
from pathlib import Path

# Add backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting AlphaCode API with WebSocket support...")
    print("📡 WebSocket endpoint: ws://localhost:8000/ws/chat")
    print("💚 Health check: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop")
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
