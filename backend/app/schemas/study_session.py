from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SessionCreate(BaseModel):
    session_date: date
    minutes: int = Field(gt=0, le=1440)
    note: str | None = Field(default=None, max_length=500)

    @field_validator("session_date")
    @classmethod
    def not_in_future(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("session_date cannot be in the future")
        return value


class SessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    topic_id: int
    session_date: date
    minutes: int
    note: str | None