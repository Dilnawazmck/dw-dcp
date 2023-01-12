from typing import List

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas import survey as survey_schema
from app.services import authentication
from app.services.question import _question
from app.services.survey import _survey
from app.utils.app_utils import _hash, hash_response

router = APIRouter()


# @router.get("/", response_model=List[survey_schema.Survey])
# async def survey_list(client_id: str, db: Session = Depends(get_db_session)):
#     response = _survey.get_surveys_filter_by_client(client_id=client_id, db=db)
#     for resp in response:
#         hash_response(resp, ["id", "client_id"])
#     return response


@router.get("/{survey_id}", response_model=survey_schema.Survey)
async def get_survey_by_id(
    survey_id,
    db: Session = Depends(get_db_session),
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
):
    authentication.verify_user_role_survey(token=token, db=db, survey_id=survey_id)
    decoded_survey_id = _hash.decode(survey_id)
    if not decoded_survey_id:
        return {}
    survey_obj = _survey.get_by_id(decoded_survey_id, db)
    hash_response(survey_obj, ["id"])
    return survey_obj


@router.get(
    "/{survey_id}/questions", response_model=List[survey_schema.SurveyQuestions]
)
async def get_survey_questions(
    survey_type: int,
    survey_id: str,
    db: Session = Depends(get_db_session),
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
):
    authentication.verify_user_role_survey(token=token, db=db, survey_id=survey_id)
    survey_obj = _question.get_survey_questions(survey_id, survey_type, db)
    return survey_obj
