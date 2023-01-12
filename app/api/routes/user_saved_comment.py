from typing import List

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas import user_saved_comment as user_saved_comment_schema
from app.services import authentication
from app.services.user import _user
from app.services.user_saved_comment import _user_saved_comment
from app.utils.constants import DEFAULTFOLDER, FolderUpperCap
from app.utils.dict_utils import safe_get

router = APIRouter()


@router.get("/folder-list")
async def get_user_folder_list(
    survey_id: str,
    survey_type: int,
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    db: Session = Depends(get_db_session),
):
    authentication.verify_user_role_survey(token=token, db=db, survey_id=survey_id)

    user_email = authentication.get_current_user(token)
    authentication.verify_user_role_survey(token=token, db=db, survey_id=survey_id)
    user = _user.get_by_email(user_email=user_email, db=db)
    response = _user_saved_comment.get_by_user_folder_list(
        user_id=user.id, survey_id=survey_id, survey_type=survey_type, db=db
    )
    response = safe_get(response, "data")
    return response


@router.post("/")
async def save_comment(
    data: user_saved_comment_schema.SaveCommentIn,
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    db: Session = Depends(get_db_session),
):
    authentication.verify_user_role_survey_response(
        token=token, db=db, response_id=data.response_id
    )
    user_email = authentication.get_current_user(token)
    user = _user.get_by_email(user_email=user_email, db=db)
    is_already_saved = _user_saved_comment.get_by_user_id_and_response_id(
        user_id=user.id, response_id=data.response_id, db=db
    )
    survey_obj = _user_saved_comment.get_survey_id_survey_type(
        response_id=data.response_id, db=db
    )

    if is_already_saved:
        return is_already_saved

    if data.folder_name.strip() == "":
        data.folder_name = DEFAULTFOLDER

    obj_in = user_saved_comment_schema.SaveComment(
        response_id=data.response_id,
        user_id=user.id,
        folder_name=data.folder_name.strip(),
    )
    resp = _user_saved_comment.get_by_user_folder_list(
        user_id=user.id,
        survey_id=survey_obj.survey_id,
        survey_type=survey_obj.type,
        db=db,
    )

    if not resp:
        response = _user_saved_comment.create(db=db, obj_in=obj_in)
        return {"id": response.id, "response_id": response.response_id}
    else:
        for i in resp["data"]:
            if i["folder_name"] == data.folder_name.strip():
                response = _user_saved_comment.create(db=db, obj_in=obj_in)
                return {"id": response.id, "response_id": response.response_id}

        total_folders = resp["Total_folders"]

        if total_folders + 1 > FolderUpperCap:
            return "Maximum limit of creating folders has been reached!!"
        else:
            response = _user_saved_comment.create(db=db, obj_in=obj_in)
            return {"id": response.id, "response_id": response.response_id}


@router.delete("/{response_id}")
async def delete_saved_comment(
    response_id: int,
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    db: Session = Depends(get_db_session),
):
    authentication.verify_user_role_survey_response(
        token=token, db=db, response_id=response_id
    )

    user_email = authentication.get_current_user(token)
    user = _user.get_by_email(user_email=user_email, db=db)
    _user_saved_comment.remove_by_user_id_and_response_id(
        user_id=user.id, response_id=response_id, db=db
    )
    return {"success": True}


@router.delete("/{survey_id}/reset-saved-comments")
async def reset_all_saved_comment(
    survey_type: int,
    survey_id: str,
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    db: Session = Depends(get_db_session),
):
    authentication.verify_user_role_survey(token=token, db=db, survey_id=survey_id)
    user_email = authentication.get_current_user(token)
    user = _user.get_by_email(user_email=user_email, db=db)
    _user_saved_comment.remove_comments_by_user_id_survey_id(
        user_id=user.id, survey_id=survey_id, db=db, survey_type=survey_type
    )

    return {"success": True}
