from datetime import date

from sqlalchemy import CheckConstraint, Date, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Topic(Base):
    __tablename__ = "topics"
    __table_args__ = (
        CheckConstraint("priority BETWEEN 1 AND 3", name="ck_topic_priority"),
        CheckConstraint("planned_hours > 0", name="ck_topic_hours"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    goal_id: Mapped[int] = mapped_column(
        ForeignKey("goals.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(200))
    priority: Mapped[int] = mapped_column(default=2)
    planned_hours: Mapped[float] = mapped_column(Float)
    deadline: Mapped[date] = mapped_column(Date)

    goal: Mapped["Goal"] = relationship(back_populates="topics")
    sessions: Mapped[list["StudySession"]] = relationship(
        back_populates="topic", cascade="all, delete-orphan", passive_deletes=True
    )