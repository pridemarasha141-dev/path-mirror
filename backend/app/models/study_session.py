from datetime import date

from sqlalchemy import CheckConstraint, Date, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class StudySession(Base):
    __tablename__ = "sessions"
    __table_args__ = (CheckConstraint("minutes > 0", name="ck_session_minutes"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int] = mapped_column(
        ForeignKey("topics.id", ondelete="CASCADE"), index=True
    )
    session_date: Mapped[date] = mapped_column(Date)
    minutes: Mapped[int]
    note: Mapped[str | None] = mapped_column(Text)

    topic: Mapped["Topic"] = relationship(back_populates="sessions")