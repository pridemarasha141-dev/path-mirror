from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """All models inherit from this; it collects their table definitions."""


def get_db():
    """FastAPI dependency: one DB session per request, always closed after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()