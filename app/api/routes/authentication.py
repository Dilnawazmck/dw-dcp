from datetime import timedelta

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES
from app.db.session import get_db_session
from app.schemas import authentication as auth_schema
from app.services import authentication

router = APIRouter()


@router.get(
    "/access-token",
    response_model=auth_schema.AccessToken,
)
async def get_access_and_refresh_token(
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token_via_okta),
    db: Session = Depends(get_db_session),
):
    role = authentication.fetch_role(token, db)
    access_token: str = authentication.create_token(
        token, role, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token: str = authentication.create_token(
        token, role, expires_delta=timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    )
    return JSONResponse(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
        }
    )


@router.get(
    "/refresh-token",
    response_model=auth_schema.RefreshToken,
)
async def refresh_token(
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
):
    access_token = authentication.create_token(
        token,
        None,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        is_refresh=True,
    )
    return JSONResponse({"access_token": access_token, "token_type": "Bearer"})
