from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class TopicCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    priority: int = Field(default=2, ge=1, le=3)
    planned_hours: float = Field(gt=0, le=10000)
    deadline: date


class TopicUpdate(TopicCreate):
    """PUT replaces all fields, so it has the same shape as create."""


class TopicOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    goal_id: int
    name: str
    priority: int
    planned_hours: float
    deadline: date