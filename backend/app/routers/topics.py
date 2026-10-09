from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_owned_goal, get_owned_topic
from app.db.session import get_db
from app.models.goal import Goal
from app.models.topic import Topic
from app.schemas.topic import TopicCreate, TopicOut, TopicUpdate

router = APIRouter(tags=["topics"])


def _check_deadline(goal: Goal, data: TopicCreate) -> None:
    # The analysis divides by (deadline - goal start), so it must be positive.
    if data.deadline <= goal.start_date:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Topic deadline must be after the goal's start date",
        )


@router.post(
    "/goals/{goal_id}/topics",
    response_model=TopicOut,
    status_code=status.HTTP_201_CREATED,
)
def create_topic(
    data: TopicCreate,
    goal: Goal = Depends(get_owned_goal),
    db: Session = Depends(get_db),
):
    _check_deadline(goal, data)
    topic = Topic(goal_id=goal.id, **data.model_dump())
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic


@router.get("/goals/{goal_id}/topics", response_model=list[TopicOut])
def list_topics(goal: Goal = Depends(get_owned_goal), db: Session = Depends(get_db)):
    return db.scalars(
        select(Topic).where(Topic.goal_id == goal.id).order_by(Topic.deadline, Topic.id)
    ).all()


@router.put("/topics/{topic_id}", response_model=TopicOut)
def update_topic(
    data: TopicUpdate,
    topic: Topic = Depends(get_owned_topic),
    db: Session = Depends(get_db),
):
    _check_deadline(topic.goal, data)
    for field, value in data.model_dump().items():
        setattr(topic, field, value)
    db.commit()
    db.refresh(topic)
    return topic


@router.delete("/topics/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_topic(topic: Topic = Depends(get_owned_topic), db: Session = Depends(get_db)):
    db.delete(topic)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)