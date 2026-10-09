from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_owned_goal, get_owned_study_session, get_owned_topic
from app.db.session import get_db
from app.models.goal import Goal
from app.models.study_session import StudySession
from app.models.topic import Topic
from app.schemas.study_session import SessionCreate, SessionOut

router = APIRouter(tags=["sessions"])


@router.post(
    "/topics/{topic_id}/sessions",
    response_model=SessionOut,
    status_code=status.HTTP_201_CREATED,
)
def log_session(
    data: SessionCreate,
    topic: Topic = Depends(get_owned_topic),
    db: Session = Depends(get_db),
):
    study_session = StudySession(topic_id=topic.id, **data.model_dump())
    db.add(study_session)
    db.commit()
    db.refresh(study_session)
    return study_session


@router.get("/goals/{goal_id}/sessions", response_model=list[SessionOut])
def list_goal_sessions(
    goal: Goal = Depends(get_owned_goal), db: Session = Depends(get_db)
):
    return db.scalars(
        select(StudySession)
        .join(Topic, StudySession.topic_id == Topic.id)
        .where(Topic.goal_id == goal.id)
        .order_by(StudySession.session_date.desc(), StudySession.id.desc())
    ).all()


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    study_session: StudySession = Depends(get_owned_study_session),
    db: Session = Depends(get_db),
):
    db.delete(study_session)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)