import os
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core import config
from app.core.config import AWS_BUCKET_NON_OHI_UPLOAD_API
from app.db.session import get_db_session
from app.models import Nonohi_Data
from app.schemas import nonohi_data as nonohi_data_schema
from app.services import authentication
from app.services.nonohi_data import _nonohi_data
from app.services.user import _user
from app.utils.app_utils import get_similar_words
from app.utils.aws_utils import upload_file_s3
from app.utils.constants import (
    NON_OHI_PREFIX,
    NON_OHI_REQUEST_PER_USER,
    NonOhiDataStatus,
)
from app.utils.email_utils import send_email

router = APIRouter()


@router.get("/similar")
def similar_words(
    keywords: str,
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    db: Session = Depends(get_db_session),
):
    return get_similar_words(keywords.split(","), top=15)


# @router.post("/classify")
# async def classify(
#     # data: zero_shot_classification_schema.TextClassificationSchema,
#     background_tasks: BackgroundTasks,
#     token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
# ):
#     # user_email = authentication.get_current_user(token)
#     # response = _zero_shot_service.get_most_relevant_label(
#     #     data.text, data.labels, user_email, background_tasks
#     # )
#     response = {}
#     return response


@router.post("/non-ohi/upload-file", response_model=nonohi_data_schema.NonohiDataOut)
async def upload_file(
    client_name: str,
    dataset_name: str,
    file_obj: UploadFile = File(...),
    dataset_type_id: int = 4,
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    db: Session = Depends(get_db_session),
):
    user_email = authentication.get_current_user(token)
    user = _user.get_by_email(user_email=user_email, db=db)

    dataset_by_user_result = (
        db.query(Nonohi_Data)
        .filter(
            Nonohi_Data.user_id == user.id,
            Nonohi_Data.status == NonOhiDataStatus.NEW.value,
        )
        .all()
    )

    if len(dataset_by_user_result) >= NON_OHI_REQUEST_PER_USER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Max limit of requests per user reached. Please reach out to OHI Helpdesk to clear your previous requests.",
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

    obj_in = nonohi_data_schema.NonohiData(
        user_id=user.id,
        client_name=client_name,
        dataset_name=dataset_name,
        dataset_type_id=dataset_type_id,
        status=NonOhiDataStatus.NEW.value,
    )
    nonohi_obj = _nonohi_data.create(db=db, obj_in=obj_in)

    pid = NON_OHI_PREFIX + str(nonohi_obj.id)
    s3_path = os.path.join(Path(pid), Path(file_obj.filename))

    upload_file_s3(local_file_path, AWS_BUCKET_NON_OHI_UPLOAD_API, s3_path)

    update_dict = {"pid": pid, "s3_path": s3_path}

    response = _nonohi_data.update(db_obj=nonohi_obj, update_data=update_dict, db=db)

    # send email to user
    send_email(
        "Non OHI data request",
        "Your request has been received by us. We are currently reviewing your request and will reach out to you in case we need any inputs.",
        [user_email],
    )

    # send email to helpdesk
    send_email(
        "Non OHI data request",
        "There is a new Non OHI data request. Please login to Text analytics tool to review this.",
        [config.SENDER],
    )

    return response
