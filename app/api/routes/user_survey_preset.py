from typing import List
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import get_db_session
from app.services import authentication
from app.services.user_survey_preset import _preset
from app.services.user import _user

router = APIRouter()


@router.get("/survey/{survey_id}/user-preset")
async def get_user_survey_preset(
        survey_type: int,
        survey_id: str,
        token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
        db: Session = Depends(get_db_session)
):
    authentication.verify_user_role_survey(token=token, db=db, survey_id=survey_id)
    user_email = authentication.get_current_user(token)
    user = _user.get_by_email(user_email=user_email, db=db)
    response = _preset.get_user_survey_preset(survey_id=survey_id, user_id=user.id,survey_type=survey_type, db=db)
    return response


@router.post("/survey/{survey_id}/user-preset")
async def insert_user_survey_preset(
        survey_type: int,
        survey_id: str,
        name: str,
        preset_filters: List,
        token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
        db: Session = Depends(get_db_session)
):
    authentication.verify_user_role_survey(token=token, db=db, survey_id=survey_id)
    user_email = authentication.get_current_user(token)
    user = _user.get_by_email(user_email=user_email, db=db)
    _preset.create_user_survey_preset(survey_id=survey_id, user_id=user.id, name=name,preset_filters=preset_filters,survey_type=survey_type, db=db)
    return {"success": True}


@router.delete("/survey/{survey_id}/user-preset/{preset_id}")
async def delete_preset(
        preset_id: int,
        token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
        db: Session = Depends(get_db_session),
):
    user_email = authentication.get_current_user(token)
    user = _user.get_by_email(user_email=user_email, db=db)
    _preset.verify_user_preset_survey(user_id=user.id, preset_id=preset_id, db=db)
    _preset.remove(db, id=preset_id)
    return {"success": True}



@router.put("/survey/{survey_id}/user-preset/{preset_id}")
async def edit_preset(
        preset_id: int,
        preset_filters: List,
        token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
        db: Session = Depends(get_db_session),
):
    user_email = authentication.get_current_user(token)
    user = _user.get_by_email(user_email=user_email, db=db)
    user_preset_obj = _preset.verify_user_preset_survey(user_id=user.id, preset_id=preset_id, db=db)
    update_dict = {"preset_filters": preset_filters}
    _preset.update(db_obj=user_preset_obj, update_data=update_dict, db=db)
    return {"success": True}
