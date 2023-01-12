from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.services import authentication
from app.services.user import _user
from app.services.user_topics import _user_topics
from app.services.custom_topics_job import _custom_topics_job

router = APIRouter()


@router.get("/custom-topics-job/status")
async def get_user_topics_job_status(
    survey_id: str,
    db: Session = Depends(get_db_session),
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
):
    authentication.verify_user_role_survey(token=token, db=db, survey_id=survey_id)
    user_email = authentication.get_current_user(token)
    user = _user.get_by_email(user_email=user_email, db=db)

    user_topics_obj = _user_topics.get_user_topics_by_user_id_and_survey_id(user_id=user.id, survey_id=survey_id, db=db)

    completion_time = _custom_topics_job.get_job_completion_time(survey_id=survey_id, db=db)
    if not completion_time:
        return None

    if not user_topics_obj:
        return {"message": completion_time,
                "secondary_message": "No custom topics found."
                }

    custom_topics_job_obj = _custom_topics_job.get_latest_custom_topics_job_status(
        user_topic_id=user_topics_obj.id, db=db
    )

    if not custom_topics_job_obj:
        return {"message": completion_time,
                "secondary_message": "No jobs found."
                }

    return {"id": custom_topics_job_obj.id,
            "status": custom_topics_job_obj.status,
            "action": custom_topics_job_obj.action,
            "message": completion_time}
