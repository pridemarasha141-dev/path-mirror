from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_owned_goal
from app.db.session import get_db
from app.models.goal import Goal
from app.models.user import User
from app.schemas.goal import GoalCreate, GoalOut, GoalUpdate

router = APIRouter(prefix="/goals", tags=["goals"])


@router.post("", response_model=GoalOut, status_code=status.HTTP_201_CREATED)
def create_goal(
    data: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = Goal(user_id=current_user.id, **data.model_dump())
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@router.get("", response_model=list[GoalOut])
def list_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.scalars(
        select(Goal).where(Goal.user_id == current_user.id).order_by(Goal.id.desc())
    ).all()


@router.get("/{goal_id}", response_model=GoalOut)
def get_goal(goal: Goal = Depends(get_owned_goal)):
    return goal


@router.put("/{goal_id}", response_model=GoalOut)
def update_goal(
    data: GoalUpdate,
    goal: Goal = Depends(get_owned_goal),
    db: Session = Depends(get_db),
):
    for field, value in data.model_dump().items():
        setattr(goal, field, value)
    db.commit()
    db.refresh(goal)
    return goal


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(goal: Goal = Depends(get_owned_goal), db: Session = Depends(get_db)):
    db.delete(goal)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)