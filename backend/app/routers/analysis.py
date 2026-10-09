from fastapi import APIRouter, Depends

from app.core.deps import get_owned_goal
from app.models.goal import Goal
from app.schemas.analysis import GoalAnalysis
from app.services.analysis import analyze_goal

router = APIRouter(tags=["analysis"])


@router.get("/goals/{goal_id}/analysis", response_model=GoalAnalysis)
def goal_analysis(goal: Goal = Depends(get_owned_goal)):
    return analyze_goal(goal)