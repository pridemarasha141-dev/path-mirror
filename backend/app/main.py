from app.routers import auth, goals, sessions, topics
from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(title=settings.app_name)
app.include_router(auth.router)
app.include_router(goals.router)
app.include_router(topics.router)
app.include_router(sessions.router)

@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name}