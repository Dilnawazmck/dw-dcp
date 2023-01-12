import json

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas import exclude_keywords as exclude_keywords_schema
from app.services import authentication
from app.services.exclude_keywords import _exclude_keywords
from app.services.user import _user
from app.utils.app_utils import _hash

router = APIRouter()


@router.get(
    "/{survey_id}/exclude-keywords",
    response_model=exclude_keywords_schema.ExcludeKeywordOut,
)
def get_exclude_keyword(
    survey_id: str,
    db: Session = Depends(get_db_session),
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
):
    user_email = authentication.get_current_user(token)
    user = _user.get_by_email(user_email=user_email, db=db)
    authentication.verify_user_role_survey(token=token, db=db, survey_id=survey_id)
    decoded_survey_id = _hash.decode(survey_id)
    if not decoded_survey_id[0]:
        return None
    db_result = _exclude_keywords.get_exclude_keywords(
        decoded_survey_id[0], user.id, db
    )
    return db_result


@router.post("/{survey_id}/insert-exclude-keywords")
def add_exclude_keyword(
    survey_id: str,
    exc_keyword: str,
    db: Session = Depends(get_db_session),
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
):
    authentication.verify_user_role_survey(token=token, db=db, survey_id=survey_id)
    user_email = authentication.get_current_user(token)
    user = _user.get_by_email(user_email=user_email, db=db)
    decoded_survey_id = _hash.decode(survey_id)
    if not decoded_survey_id[0]:
        return None

    resp = _exclude_keywords.get_exclude_keywords(
        survey_id=decoded_survey_id[0], user_id=user.id, db=db
    )
    if not resp:
        obj = exclude_keywords_schema.ExcludeKeyword(
            survey_id=decoded_survey_id[0], user_id=user.id, keyword=[exc_keyword]
        )
        _exclude_keywords.create(obj_in=obj, db=db)
    else:
        if not (exc_keyword in resp.keyword):
            updated_list = resp.keyword
            updated_list.append(exc_keyword)

            obj = exclude_keywords_schema.ExcludeKeyword(
                survey_id=decoded_survey_id[0], user_id=user.id, keyword=resp.keyword
            )
            final_keyword = json.dumps(obj.keyword)
            final_keyword2 = json.loads(final_keyword)
            _exclude_keywords.update_exclude_keyword(
                survey_id=decoded_survey_id[0],
                user_id=user.id,
                db=db,
                exclude_keyword=final_keyword2,
            )
    return {"success": True}
