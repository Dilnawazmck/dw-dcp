from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db_session

from app.schemas import user_topics as user_topics_schema
from app.schemas import custom_topics_job as custom_topics_job_schema
from app.services import authentication
from app.services.user import _user
from app.services.user_topics import _user_topics
from app.services.custom_topics_job import _custom_topics_job
from app.services.celery_service.classifier import custom_topic_classification
from app.utils.constants import CustomTopicsJobStatus, CustomTopicsJobAction


router = APIRouter()


@router.get("/survey/{survey_id}/user-topics", response_model=user_topics_schema.GetUserTopics)
def get_user_topics(
    survey_id: str,
    db: Session = Depends(get_db_session),
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
):
    authentication.verify_user_role_survey(token=token, db=db, survey_id=survey_id)
    user_email = authentication.get_current_user(token)
    user_obj = _user.get_by_email(user_email=user_email, db=db)

    response = _user_topics.get_user_topics_by_user_id_and_survey_id(user_id=user_obj.id, survey_id=survey_id, db=db)

    return response


@router.post("/survey/{survey_id}/user-topics")
def create_user_topics(
    survey_id: str,
    topic_list: List,
    db: Session = Depends(get_db_session),
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
):
    authentication.verify_user_role_survey(token=token, db=db, survey_id=survey_id)
    user_email = authentication.get_current_user(token)
    user_obj = _user.get_by_email(user_email=user_email, db=db)

    user_topics_obj = _user_topics.create_user_topic_list(user_obj.id, survey_id, topic_list, db=db)

    obj_custom_topics_job_in = custom_topics_job_schema.AddCustomTopicsJob(
        user_topic_id=user_topics_obj.id, survey_id=user_topics_obj.survey_id,
        status=CustomTopicsJobStatus.QUEUE.value,
        action=CustomTopicsJobAction.CREATE.value
    )
    job_obj = _custom_topics_job.create(db=db, obj_in=obj_custom_topics_job_in)

    custom_topic_classification.delay(job_obj.id)

    return {"message": "Your topics list has been added. Once you data has been re-processed you will be notified "
                       "via an email"}


@router.put("/survey/{survey_id}/user-topics")
def edit_user_topics(
    survey_id: str,
    topic_list: List,
    db: Session = Depends(get_db_session),
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
):
    authentication.verify_user_role_survey(token=token, db=db, survey_id=survey_id)
    user_email = authentication.get_current_user(token)
    user_obj = _user.get_by_email(user_email=user_email, db=db)

    user_topics_obj = _user_topics.get_user_topics_by_user_id_and_survey_id(user_id=user_obj.id, survey_id=survey_id,
                                                                            db=db)
    _custom_topics_job.is_custom_topics_job_pending(user_topic_id=user_topics_obj.id, db=db)

    _user_topics.update_user_topics(user_topics_obj=user_topics_obj, topics_list=topic_list, db=db)

    obj_custom_topics_job_in = custom_topics_job_schema.AddCustomTopicsJob(
        user_topic_id=user_topics_obj.id, survey_id=user_topics_obj.survey_id,
        status=CustomTopicsJobStatus.QUEUE.value,
        action=CustomTopicsJobAction.MODIFY.value
    )
    job_obj = _custom_topics_job.create(db=db, obj_in=obj_custom_topics_job_in)

    custom_topic_classification.delay(job_obj.id, True)

    return {"message": "Your topics list has been updated successfully. Once you data has been re-processed you will be"
                       " notified via an email"}


@router.get("/response/{survey_id}/user-topics-sentiment-count")
def get_sentiment_counts_by_user_topics(
    survey_id: str,
    db: Session = Depends(get_db_session),
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    filters="",
):
    authentication.verify_user_role_survey(token=token, db=db, survey_id=survey_id)
    user_email = authentication.get_current_user(token)
    user_obj = _user.get_by_email(user_email=user_email, db=db)
    response =_user_topics.get_sentiment_counts_by_user_topic(user_obj.id, survey_id, filters, db)
    return response


@router.get("/response/{survey_id}/user-topics-counts")
def get_counts_in_survey_by_user_topics(
    survey_id: str,
    db: Session = Depends(get_db_session),
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    filters="",
):
    authentication.verify_user_role_survey(token=token, db=db, survey_id=survey_id)
    user_email = authentication.get_current_user(token)
    user_obj = _user.get_by_email(user_email=user_email, db=db)

    grouped_comments_count: list = _user_topics.get_counts_in_survey_user_topics(
        user_obj.id, survey_id, filters, db
    )
    response = {
        "total_comments": sum([row["count"] for row in grouped_comments_count]),
        "data": grouped_comments_count,
    }
    return response


@router.get("/response/{survey_id}/user-topics-popular-words")
def get_popular_words_by_user_topics(
    survey_id: str,
    db: Session = Depends(get_db_session),
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    filters=None,
):
    authentication.verify_user_role_survey(token=token, db=db, survey_id=survey_id)
    user_email = authentication.get_current_user(token)
    user_obj = _user.get_by_email(user_email=user_email, db=db)

    survey_obj = _user_topics.get_popular_words_in_survey_by_user_topics(user_obj.id, survey_id, filters, db)
    return survey_obj


@router.get("/response/{survey_id}/user-topics-comments")
def get_user_topics_comments(
    survey_id: str,
    page_no: Optional[int] = 1,
    db: Session = Depends(get_db_session),
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    filters="",
):
    authentication.verify_user_role_survey(token=token, db=db, survey_id=survey_id)

    page_size = 10
    user_email = authentication.get_current_user(token)
    user_obj = _user.get_by_email(user_email=user_email, db=db)

    result = _user_topics.get_survey_responses_with_topics(
        survey_id=survey_id,
        db=db,
        filters=filters,
        user_id=user_obj.id,
        user_saved_comment_join_type="left join",
        skip=(page_no - 1) * page_size,
        limit=page_size,
    )
    return result

