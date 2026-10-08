from app.routers import auth
from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(title=settings.app_name)
app.include_router(auth.router)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name}