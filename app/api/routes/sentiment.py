from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db_session
from app.schemas import sentiment as sentiment_schema
from app.services.sentiment import _sentiment
from fastapi.security import HTTPAuthorizationCredentials
from app.services import authentication

router = APIRouter()

@router.get("/", response_model=List[sentiment_schema.Sentiment])
async def sentiment_list(
        db: Session = Depends(get_db_session),
        token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
):
    response = _sentiment.get_all(db)
    return response
