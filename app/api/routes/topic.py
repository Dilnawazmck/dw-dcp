from typing import List

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas import topic as topic_schema
from app.services import authentication
from app.services.topic import _topic

router = APIRouter()


@router.get("/", response_model=List[topic_schema.Topic])
async def topic_list(
    db: Session = Depends(get_db_session),
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
):
    response = _topic.get_all(db)
    return response
