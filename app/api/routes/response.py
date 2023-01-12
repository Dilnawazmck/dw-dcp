from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas import response as response_schema
from app.schemas import user_classified_comment as user_classified_comment_schema
from app.services import authentication
from app.services.response import _response
from app.services.user import _user
from app.services.user_classified_comment import _user_classified_comment
from app.utils import str_utils

router = APIRouter()


@router.get("/{survey_id}/popular-words")
def get_top_words_by_survey_id(
    survey_id: str,
    group_by: str,
    db: Session = Depends(get_db_session),
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    filters=None,
):
    authentication.verify_user_role_survey(token=token, db=db, survey_id=survey_id)

    survey_obj = _response.get_popular_words_in_survey(survey_id, group_by, filters, db)
    return survey_obj


@router.get("/{survey_id}/sentiment-count")
def get_sentiment_count(
    survey_id: str,
    group_by: str,
    db: Session = Depends(get_db_session),
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    filters=None,
    sortby="Positive:desc",
):
    authentication.verify_user_role_survey(token=token, db=db, survey_id=survey_id)

    survey_obj = _response.get_sentiment_count_in_survey(
        survey_id, group_by, filters, db, sortby
    )
    return survey_obj


@router.get("/{survey_id}/sentiment-breakdown")
def get_sentiment_breakdown(
    survey_id: str,
    db: Session = Depends(get_db_session),
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    filters=None,
):
    authentication.verify_user_role_survey(token=token, db=db, survey_id=survey_id)
    survey_obj = _response.get_sentiment_breakdown(survey_id, filters, db)
    return survey_obj


@router.get("/{survey_id}/sentiment-wise-demographic")
def get_sentiment_wise_demographic(
    survey_id: str,
    db: Session = Depends(get_db_session),
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    filters=None,
    demographic: str = "overall",
    sentiment: str = "Positive:desc",
    nsize: str = "gt:0",
    page_no: int = 1,
):
    page_size = 10
    limit = 10
    authentication.verify_user_role_survey(token=token, db=db, survey_id=survey_id)
    survey_obj = _response.get_sentiment_wise_demographic_scores(
        survey_id=survey_id,
        filters=filters,
        demographic=demographic,
        sentiment=sentiment,
        nsize=nsize,
        skip=(page_no - 1) * page_size,
        limit=limit,
        db=db,
    )
    return survey_obj


@router.get("/{survey_id}/swd-scores-popup-data")
def get_sentiment_wise_demographic_popup_data(
    survey_id: str,
    db: Session = Depends(get_db_session),
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    filters=None,
    demographic: str = ""
):
    limit=5
    authentication.verify_user_role_survey(token=token, db=db, survey_id=survey_id)
    survey_obj = _response.get_swd_pop_data(
        survey_id=survey_id,
        filters=filters,
        demographic=demographic,
        limit=limit,
        db=db,
    )
    return survey_obj

#
# @router.get("/{survey_id}/sentiment-wise-demographic")
# def get_sentiment_wise_demographic(
#     survey_id: str,
#     db: Session = Depends(get_db_session),
#     token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
#     filters=None,
#     demographic: str = "overall",
#     sentiment: str = "Positive:desc",
#     nsize: str = "gt:0",
#     page_no: int = 1,
# ):
#     page_size = 10
#     limit = 10
#     authentication.verify_user_role_survey(token=token, db=db, survey_id=survey_id)
#     survey_obj = _response.get_sentiment_wise_demographic(
#         survey_id=survey_id,
#         filters=filters,
#         demographic=demographic,
#         sentiment=sentiment,
#         nsize=nsize,
#         skip=(page_no - 1) * page_size,
#         limit=limit,
#         db=db,
#     )
#     return survey_obj


@router.get("/{survey_id}/sentiment-mention-matrix")
def get_sentiment_mention_matrix(
    survey_id: str,
    db: Session = Depends(get_db_session),
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    filters=None,
    group_by="practice_id",
):
    authentication.verify_user_role_survey(token=token, db=db, survey_id=survey_id)
    survey_obj = _response.get_sentiment_mention_matrix(
        survey_id=survey_id, filters=filters, group_by=group_by, db=db
    )
    return survey_obj


# @router.get("/{survey_id}/sentiment-mention-matrix_popup")
# def get_sentiment_mention_matrix_popup(
#     survey_id: str,
#     group_by_id:int,
#     db: Session = Depends(get_db_session),
#     token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
#     filters=None,
#     group_by="practice_id"
# ):
#     authentication.verify_user_role_survey(token=token, db=db, survey_id=survey_id)
#     survey_obj = _response.get_sentiment_mention_matrix_popup(
#         survey_id=survey_id, filters=filters, group_by=group_by,db=db,group_by_id=group_by_id
#     )
#     return survey_obj


@router.get("/{survey_id}/demographic-heatmap")
def get_demographic_heatmap(
    survey_id: str,
    db: Session = Depends(get_db_session),
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    filters=None,
    demographic="",
    group_by="practice_id",
    page_no: int = 1,
):
    page_size = 10
    limit = 10

    authentication.verify_user_role_survey(token=token, db=db, survey_id=survey_id)
    survey_obj = _response.get_demographic_heatmap(
        survey_id=survey_id,
        filters=filters,
        group_by=group_by,
        demographic=demographic,
        skip=(page_no - 1) * page_size,
        limit=limit,
        db=db,
    )
    return survey_obj


@router.get("/{survey_id}/counts")
def get_counts_in_survey(
    survey_id: str,
    group_by: str,
    db: Session = Depends(get_db_session),
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    filters="",
    mention_type="low",
):
    authentication.verify_user_role_survey(token=token, db=db, survey_id=survey_id)

    order_by = "desc"

    if mention_type == "high":
        mention_type = ">"
        order_by = "desc"

    if mention_type == "low":
        mention_type = "<"
        order_by = "asc"

    grouped_comments_count: list = _response.get_comments_in_survey_group_by(
        survey_id, group_by, filters, mention_type, order_by, db
    )
    response = {
        "total_comments": sum([row["count"] for row in grouped_comments_count]),
        "data": grouped_comments_count,
    }
    return response


@router.get("/{survey_id}/comments")
def get_survey_comments(
    survey_id: str,
    page_no: Optional[int] = 1,
    db: Session = Depends(get_db_session),
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    filters="",
    folder_name="",
    order_by: str = "practice",
):
    authentication.verify_user_role_survey(token=token, db=db, survey_id=survey_id)

    page_size = 10
    user_email = authentication.get_current_user(token)
    user = _user.get_by_email(user_email=user_email, db=db)

    result = _response.get_survey_responses(
        survey_id=survey_id,
        db=db,
        filters=filters,
        user_id=user.id,
        folder_name=folder_name,
        user_saved_comment_join_type="left join",
        skip=(page_no - 1) * page_size,
        limit=page_size,
        order_by=order_by,
    )
    return result


@router.get("/{survey_id}/saved-comments")
def get_saved_survey_comments(
    survey_id: str,
    page_no: Optional[int] = 1,
    db: Session = Depends(get_db_session),
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    filters="",
    folder_name="",
    order_by: str = "practice",
):
    authentication.verify_user_role_survey(token=token, db=db, survey_id=survey_id)

    page_size = 10
    user_email = authentication.get_current_user(token)
    user = _user.get_by_email(user_email=user_email, db=db)
    filters += str_utils.safe_concat(
        ";" if filters else None, str_utils.safe_concat("user_id:eq:", user.id)
    )
    result = _response.get_survey_responses(
        survey_id=survey_id,
        db=db,
        filters=filters,
        user_id=user.id,
        user_saved_comment_join_type="join",
        skip=(page_no - 1) * page_size,
        limit=page_size,
        folder_name=folder_name,
        order_by=order_by,
    )
    return result


@router.get("/{survey_id}/wordcloud")
def get_survey_wordcloud(
    survey_id: str,
    limit: Optional[int] = 50,
    db: Session = Depends(get_db_session),
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    filters=None,
):
    authentication.verify_user_role_survey(token=token, db=db, survey_id=survey_id)

    result = _response.get_survey_wordcloud(survey_id, db, filters, limit=limit)
    return result


@router.put("/{survey_id}/reclassify", response_model=response_schema.ReclassifyOut)
def reclassify_comment(
    survey_id: str,
    data: response_schema.ReclassifyIn,
    db: Session = Depends(get_db_session),
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
):
    authentication.verify_user_role_survey(token=token, db=db, survey_id=survey_id)
    user_email = authentication.get_current_user(token)
    user = _user.get_by_email(user_email=user_email, db=db)

    resp_obj = _response.get_by_id_and_survey_id(
        id=data.response_id, survey_id=survey_id, db=db
    )
    update_dict = {}
    if data.topic_id:
        update_dict["topic_id"] = data.topic_id
        update_dict["is_topic_verified"] = True
    if data.practice_id:
        update_dict["practice_id"] = data.practice_id
        update_dict["is_practice_verified"] = True
    if data.sentiment_id:
        update_dict["sentiment_id"] = data.sentiment_id
        update_dict["is_sentiment_verified"] = True
        # update_dict["sentiment_score"] = 1
    updated_obj = _response.update(db_obj=resp_obj, update_data=update_dict, db=db)

    user_classify_obj = _user_classified_comment.get_by_user_id_response_id(
        user_id=user.id, response_id=resp_obj.id, db=db
    )

    if user_classify_obj:
        update_user_classify_dict = {
            "last_updated_on": datetime.now(),
            "user_id": user.id,
            "response_id": resp_obj.id,
        }
        _user_classified_comment.update(
            db_obj=user_classify_obj, update_data=update_user_classify_dict, db=db
        )
    else:
        create_obj_in = user_classified_comment_schema.UserClassifyComment(
            user_id=user.id, response_id=resp_obj.id
        )
        _user_classified_comment.create(db=db, obj_in=create_obj_in)

    return updated_obj


@router.get("/{survey_id}/export", response_description="xlsx")
def get_survey_excel(
    survey_id: str,
    db: Session = Depends(get_db_session),
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    filters="",
    is_saved_comments: bool = False,
    excel_name: str = "export",
):
    authentication.verify_user_role_survey(token=token, db=db, survey_id=survey_id)
    user_email = authentication.get_current_user(token)
    user = _user.get_by_email(user_email=user_email, db=db)
    result = _response.get_survey_excel(
        survey_id,
        db,
        filters,
        user_id=user.id,
        is_saved_comments=is_saved_comments,
        excel_name=excel_name,
    )

    return result
