import io
import os
import tempfile
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import AWS_BUCKET_NON_OHI_UPLOAD_API, AWS_BUCKET_TRANSFORM
from app.db.session import get_db_session
from app.schemas import nonohi_data as nonohi_data_schema
from app.schemas import role as role_schema
from app.schemas import user as user_schema
from app.schemas import user_survey as user_survey_schema
from app.services import authentication
from app.services.nonohi_data import _nonohi_data
from app.services.user import _user
from app.services.user_survey import _user_survey
from app.utils.app_utils import _hash
from app.utils.aws_utils import copy_file, download_directory, upload_file_s3
from app.utils.constants import NonOhiDataStatus
from app.utils.email_utils import send_email

router = APIRouter()


@router.get("/users")
def get_users(
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    db: Session = Depends(get_db_session),
):
    user_email = authentication.get_current_user(token)
    user = _user.get_by_email(user_email=user_email, db=db)
    if not _user.is_authorized(user.role_id, db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to perform this action.",
        )

    result = _user.get_users(db)
    return result


@router.get("/roles", response_model=List[role_schema.Role])
def get_roles(
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    db: Session = Depends(get_db_session),
):
    user_email = authentication.get_current_user(token)
    user = _user.get_by_email(user_email=user_email, db=db)
    if not _user.is_authorized(user.role_id, db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to perform this action.",
        )

    result = _user.get_roles(db)
    return result


@router.post("/user", response_model=user_schema.AddUserOut)
async def add_user(
    data: user_schema.AddUserIn,
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    db: Session = Depends(get_db_session),
):
    current_user_email = authentication.get_current_user(token)
    current_user = _user.get_by_email(user_email=current_user_email, db=db)
    if not _user.is_authorized(current_user.role_id, db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to perform this action.",
        )

    if not _user.is_allowed(current_user.role_id, data.role_id, db=db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to perform this action.",
        )

    is_already_saved = _user.get_by_email(user_email=data.email, db=db)
    if is_already_saved:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )

    obj_in = user_schema.AddUser(
        email=data.email, full_name=data.full_name, role_id=data.role_id
    )
    response = _user.create_or_update(db=db, obj_in=obj_in)
    return response


@router.put("/user", response_model=user_schema.AddUserOut)
async def edit_user(
    data: user_schema.EditUserIn,
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    db: Session = Depends(get_db_session),
):
    current_user_email = authentication.get_current_user(token)
    current_user = _user.get_by_email(user_email=current_user_email, db=db)
    if not _user.is_authorized(current_user.role_id, db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to perform this action.",
        )

    user_obj = _user.get_by_id(user_id=data.id, db=db)
    if not _user.is_allowed(current_user.role_id, user_obj.role_id, db=db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to perform this action.",
        )

    update_dict = {}
    if data.email:
        update_dict["email"] = data.email
    if data.full_name:
        update_dict["full_name"] = data.full_name
    if data.role_id:
        update_dict["role_id"] = data.role_id

    response = _user.update(db_obj=user_obj, update_data=update_dict, db=db)

    return response


@router.delete("/user/{user_id}")
def delete_user(
    user_id: str,
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    db: Session = Depends(get_db_session),
):
    current_user_email = authentication.get_current_user(token)
    current_user = _user.get_by_email(user_email=current_user_email, db=db)
    if not _user.is_authorized(current_user.role_id, db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to perform this action.",
        )

    user_obj = _user.get_by_id(user_id=user_id, db=db)
    if not _user.is_allowed(current_user.role_id, user_obj.role_id, db=db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to perform this action.",
        )

    _user.update(db_obj=user_obj, update_data={"is_deleted": True}, db=db)
    return {"success": True}


@router.get("/{user_id}/user-detail")
def get_user_details(
    user_id: str,
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    db: Session = Depends(get_db_session),
):
    current_user_email = authentication.get_current_user(token)
    current_user = _user.get_by_email(user_email=current_user_email, db=db)
    if not _user.is_authorized(current_user.role_id, db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to perform this action.",
        )

    user_obj = _user.get_by_id(user_id=user_id, db=db)
    if not _user.is_allowed(current_user.role_id, user_obj.role_id, db=db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to perform this action.",
        )
    result = _user.get_user_details(user_id, db)
    return result


@router.post("/user-survey")
async def add_user_survey(
    data: user_survey_schema.AddUserSurveyIn,
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    db: Session = Depends(get_db_session),
):
    current_user_email = authentication.get_current_user(token)
    current_user = _user.get_by_email(user_email=current_user_email, db=db)
    if not _user.is_authorized(current_user.role_id, db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to perform this action.",
        )

    user_obj = _user.get_by_id(user_id=data.user_id, db=db)
    if not _user.is_allowed(current_user.role_id, user_obj.role_id, db=db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to perform this action.",
        )

    response = _user_survey.add_user_survey(data, db=db)
    return response


@router.put("/user-survey")
def delete_survey(
    data: user_survey_schema.DeleteUserSurveyIn,
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    db: Session = Depends(get_db_session),
):
    current_user_email = authentication.get_current_user(token)
    current_user = _user.get_by_email(user_email=current_user_email, db=db)
    if not _user.is_authorized(current_user.role_id, db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to perform this action.",
        )

    user_obj = _user.get_by_id(user_id=data.user_id, db=db)
    if not _user.is_allowed(current_user.role_id, user_obj.role_id, db=db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to perform this action.",
        )
    if data.is_delete:
        _user_survey.remove_by_user_id_and_survey_id(data, db=db)
    return {"success": True}


@router.get("/non-ohi/list")
def get_non_ohi_upload_list(
    limit: Optional[int] = 100,
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    db: Session = Depends(get_db_session),
):
    current_user_email = authentication.get_current_user(token)
    current_user = _user.get_by_email(user_email=current_user_email, db=db)
    if not _user.is_authorized(current_user.role_id, db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to perform this action.",
        )

    non_ohi_list = _nonohi_data.get_all_order_by(db=db, limit=limit)

    response = [
        {
            "id": _hash.encode(item.id),
            "created_on": item.created_on,
            "name": item.user.full_name,
            "email": item.user.email,
            "client_name": item.client_name,
            "dataset_name": item.dataset_name,
            "s3_path": item.s3_path,
            "status": item.status,
        }
        for item in non_ohi_list
    ]

    return response


@router.get("/non-ohi/download-file")
def get_file_from_s3(
    non_ohi_id: str,
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    db: Session = Depends(get_db_session),
):
    current_user_email = authentication.get_current_user(token)
    current_user = _user.get_by_email(user_email=current_user_email, db=db)
    if not _user.is_authorized(current_user.role_id, db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to perform this action.",
        )

    decoded_non_ohi_id = _hash.decode(non_ohi_id)
    if not decoded_non_ohi_id:
        return None

    nonohi_obj = _nonohi_data.get_by_id(id=decoded_non_ohi_id[0], db=db)

    if not nonohi_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not found.",
        )

    temp_base_folder = tempfile.TemporaryDirectory()

    download_directory(
        nonohi_obj.s3_path, temp_base_folder.name, AWS_BUCKET_NON_OHI_UPLOAD_API
    )
    local_file_path = os.path.join(
        Path(temp_base_folder.name), Path(nonohi_obj.s3_path)
    )
    # f = open(local_file_path, "rb")
    # stream = io.BytesIO(f.read())
    f_name = nonohi_obj.pid + ".xlsx"
    # response = StreamingResponse(iter([stream.getvalue()]))
    # response.headers["Content-Disposition"] = "attachment; filename={f_name}".format(
    #     f_name=f_name
    # )

    response = _nonohi_data.get_file_stream(local_file_path, f_name)

    return response


@router.post("/non-ohi/upload-file-for-transformation")
async def send_file_for_transformation(
    non_ohi_id: str = None,
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    db: Session = Depends(get_db_session),
):
    current_user_email = authentication.get_current_user(token)
    current_user = _user.get_by_email(user_email=current_user_email, db=db)
    if not _user.is_authorized(current_user.role_id, db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to perform this action.",
        )

    decoded_non_ohi_id = _hash.decode(non_ohi_id)
    if not decoded_non_ohi_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not a valid dataset.",
        )

    nonohi_obj = _nonohi_data.get_by_id(id=decoded_non_ohi_id[0], db=db)

    if not nonohi_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dataset not found.",
        )

    copy_source = {"Bucket": AWS_BUCKET_NON_OHI_UPLOAD_API, "Key": nonohi_obj.s3_path}
    copy_file(copy_source, AWS_BUCKET_TRANSFORM, nonohi_obj.s3_path)

    update_dict = {"status": NonOhiDataStatus.APPROVED.value}

    _nonohi_data.update(db_obj=nonohi_obj, update_data=update_dict, db=db)

    return {"success": True}


@router.put("/non-ohi/update-file")
async def update_file(
    non_ohi_id: str,
    file_obj: UploadFile = File(...),
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    db: Session = Depends(get_db_session),
):
    current_user_email = authentication.get_current_user(token)
    current_user = _user.get_by_email(user_email=current_user_email, db=db)
    if not _user.is_authorized(current_user.role_id, db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to perform this action.",
        )

    decoded_non_ohi_id = _hash.decode(non_ohi_id)
    if not decoded_non_ohi_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not a valid dataset.",
        )

    nonohi_obj = _nonohi_data.get_by_id(id=decoded_non_ohi_id[0], db=db)
    if not nonohi_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dataset does not exist.",
        )

    temp_base_folder = tempfile.TemporaryDirectory()
    local_file_path = os.path.join(Path(temp_base_folder.name), Path(file_obj.filename))
    with open(local_file_path, "wb") as out_file:
        content = await file_obj.read()  # async read
        out_file.write(content)  # async write
    try:
        _nonohi_data.validate_file(local_file_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    upload_file_s3(local_file_path, AWS_BUCKET_NON_OHI_UPLOAD_API, nonohi_obj.s3_path)

    send_email(
        subject="Non OHI data request",
        body_text="File updated successfully",
        receiver_emails=[current_user_email],
    )

    return {"success": True}
