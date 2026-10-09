from datetime import date

from pydantic import BaseModel


class TopicAnalysis(BaseModel):
    topic_id: int
    name: str
    priority: int
    deadline: date
    planned_hours: float
    logged_hours: float
    expected_hours: float
    planned_share_pct: float
    actual_share_pct: float
    gap_pct: float
    pace_ratio: float | None
    status: str
    progress_pct: float
    time_elapsed_pct: float


class OverallAnalysis(BaseModel):
    total_planned_hours: float
    total_logged_hours: float
    total_expected_hours: float
    pace_ratio: float | None
    status: str
    progress_pct: float
    session_count: int
    days_elapsed: int
    days_remaining: int


class GoalAnalysis(BaseModel):
    goal_id: int
    goal_title: str
    overall: OverallAnalysis
    topics: list[TopicAnalysis]
    insights: list[str]