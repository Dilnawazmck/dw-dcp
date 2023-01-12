from typing import List

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.models.practice import Practice
from app.schemas import practice as practice_schema
from app.services import authentication
from app.services.practice import _practice

router = APIRouter()


@router.get("/", response_model=List[practice_schema.Practice])
async def practice_list(
    practice_type: int = 1,
    db: Session = Depends(get_db_session),
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
):
    if practice_type == 4:
        practice_type = 1

    response = db.query(Practice).filter(Practice.type == practice_type).all()
    return response
