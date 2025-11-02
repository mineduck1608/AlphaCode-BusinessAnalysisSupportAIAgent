from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routers import conversation  # import routers
from backend.api.routers import conversation_agent  # import routers

app = FastAPI(title="AlphaCode API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# register routers
app.include_router(conversation.router, prefix="/conversation", tags=["conversation"])
app.include_router(conversation_agent.router, prefix="/conversation-agent", tags=["conversation-agent"])

@app.get("/health")
def healthcheck():
    return {"status": "ok"}
