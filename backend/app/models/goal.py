from datetime import date

from sqlalchemy import CheckConstraint, Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Goal(Base):
    __tablename__ = "goals"
    __table_args__ = (
        CheckConstraint("target_date >= start_date", name="ck_goal_dates"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    start_date: Mapped[date] = mapped_column(Date)
    target_date: Mapped[date] = mapped_column(Date)

    user: Mapped["User"] = relationship(back_populates="goals")
    topics: Mapped[list["Topic"]] = relationship(
        back_populates="goal", cascade="all, delete-orphan", passive_deletes=True
    )