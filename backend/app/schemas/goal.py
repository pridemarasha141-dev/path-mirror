from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator


class GoalCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    start_date: date
    target_date: date

    @model_validator(mode="after")
    def check_dates(self):
        if self.target_date < self.start_date:
            raise ValueError("target_date must be on or after start_date")
        return self


class GoalUpdate(GoalCreate):
    """PUT replaces all fields, so it has the same shape as create."""


class GoalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    start_date: date
    target_date: date