from typing import List

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas import feedback
from app.services import authentication
from app.services.feedback_category import _feedback_category
from app.services.user_feedback import _user_feedback

router = APIRouter()


@router.get("/categories", response_model=List[feedback.FeedbackCategory])
async def list_feedback_categories(
    db: Session = Depends(get_db_session),
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
):
    response = _feedback_category.get_all(db)
    return response


@router.post("/", response_model=feedback.FeedbackCreate)
async def create_feedback(
    feedback: feedback.FeedbackCreate,
    db: Session = Depends(get_db_session),
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
):
    authentication.verify_user_role_survey_response(token=token, db=db, response_id=feedback.response_id)

    response = _user_feedback.create(db=db, obj_in=feedback)
    return response
