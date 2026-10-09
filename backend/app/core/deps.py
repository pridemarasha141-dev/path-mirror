from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.models.topic import Topic
from app.models.study_session import StudySession
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User
from sqlalchemy import select
from app.models.goal import Goal

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise unauthorized
    user = db.get(User, user_id)
    if user is None:
        raise unauthorized
    return user
def get_owned_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Goal:
    goal = db.scalar(
        select(Goal).where(Goal.id == goal_id, Goal.user_id == current_user.id)
    )
    if goal is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Goal not found")
    return goal
def get_owned_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Topic:
    topic = db.scalar(
        select(Topic)
        .join(Goal, Topic.goal_id == Goal.id)
        .where(Topic.id == topic_id, Goal.user_id == current_user.id)
    )
    if topic is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Topic not found")
    return topic


def get_owned_study_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StudySession:
    study_session = db.scalar(
        select(StudySession)
        .join(Topic, StudySession.topic_id == Topic.id)
        .join(Goal, Topic.goal_id == Goal.id)
        .where(StudySession.id == session_id, Goal.user_id == current_user.id)
    )
    if study_session is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")
    return study_session