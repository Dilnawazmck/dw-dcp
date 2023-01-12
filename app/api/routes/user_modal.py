from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.user_modal import UserModalIn, UserModalOut
from app.services import authentication
from app.services.user import _user
from app.services.user_modal import _user_modal

router = APIRouter()


@router.get("/status")
def get_user_modal_status(
    db: Session = Depends(get_db_session),
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
):
    user_email = authentication.get_current_user(token)
    user = _user.get_by_email(user_email=user_email, db=db)
    result = _user_modal.get_user_modal_status(db=db, user_id=user.id)

    classify_modal_status = True
    default_modal_status = True
    if not result:
        return {
            "show_modal": default_modal_status,
            "show_classify_modal": classify_modal_status,
        }

    diff = datetime.now() - result["last_updated_on"]
    hours = diff.total_seconds() / 3600

    if hours <= 24:
        classify_modal_status = False

    response = {
        "show_modal": result["show_modal"],
        "show_classify_modal": classify_modal_status,
    }
    return response


@router.get("/{survey_id}/classifed-comments")
def get_comments_for_classification_modal(
    survey_id: str,
    survey_type: int = 1,
    db: Session = Depends(get_db_session),
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
):
    valid_comment_length = 10
    total_limit = 5
    user_email = authentication.get_current_user(token)
    authentication.verify_user_role_survey(token=token, db=db, survey_id=survey_id)
    user = _user.get_by_email(user_email=user_email, db=db)
    result = _user_modal.get_user_classification_comments(
        db=db,
        user_id=user.id,
        survey_type=survey_type,
        survey_id=survey_id,
        length=valid_comment_length,
        total_limit=total_limit,
    )
    return result


@router.post("/", response_model=UserModalOut)
async def insert_user_modal_status(
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    db: Session = Depends(get_db_session),
):
    user_email = authentication.get_current_user(token)
    user = _user.get_by_email(user_email=user_email, db=db)
    obj_in = UserModalIn(user_id=user.id, show_modal=False, show_classify_modal=False)
    is_already_save = _user_modal.get_by_user_id(user_id=user.id, db=db)

    if is_already_save:
        response = _user_modal.update(
            db_obj=is_already_save,
            update_data={
                "last_updated_on": datetime.now(),
                "show_modal": False,
                "show_classify_modal": False,
            },
            db=db,
        )
    else:
        response = _user_modal.create(db=db, obj_in=obj_in)
    return response
