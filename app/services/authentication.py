import time
from datetime import datetime, timedelta
from typing import Optional

import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.db import raw_sqls
from app.core.config import ALGORITHM, MCKID_USERINFO_URL, SECRET_KEY
from app.services.user import _user
from app.utils.constants import USER
from app.utils.app_utils import _hash


security = HTTPBearer()


def create_token(
    token: HTTPAuthorizationCredentials,
    role: str,
    expires_delta: Optional[timedelta] = None,
    is_refresh: bool = False,
):
    decoded_data = jwt.get_unverified_claims(token.credentials)
    to_encode = {
        "user": decoded_data.get("user") if is_refresh else decoded_data,
        "role": role or decoded_data.get("role"),
    }
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def fetch_role(token: HTTPAuthorizationCredentials, db: Session):
    decoded_data = jwt.get_unverified_claims(token.credentials)
    email = decoded_data.get("email")
    user_obj = _user.get_by_email(user_email=email, db=db)
    return user_obj.role.name


async def verify_token_via_okta(
    token: HTTPAuthorizationCredentials = Depends(security),
):
    headers = {"Authorization": "Bearer {}".format(token.credentials)}

    response = requests.request("POST", MCKID_USERINFO_URL, headers=headers)

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=response.json(),
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


async def verify_token(token: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("exp") < time.time():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token Expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


def verify_user_role(token: HTTPAuthorizationCredentials, db: Session):
    user_email = get_current_user(token)
    user_obj = _user.get_by_email(user_email=user_email, db=db)

    if user_obj.role.name.lower() != USER:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not Authorized",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_user_role_survey(token: HTTPAuthorizationCredentials, db: Session, survey_id: str):
    decoded_survey_id = _hash.decode(survey_id)
    if not decoded_survey_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not Authorized",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_email = get_current_user(token)
    sql_user_role_survey = raw_sqls.GET_USER_ROLES_SURVEY.format(
        user_email=user_email,
        survey_id=decoded_survey_id[0]
    )

    query_result = db.execute(statement=sql_user_role_survey).fetchone()

    if query_result[0] == 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not Authorized",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_user_role_survey_response(token: HTTPAuthorizationCredentials, db: Session, response_id: int):
    user_email = get_current_user(token)
    sql_user_role_survey_resp = raw_sqls.GET_USER_ROLES_SURVEY_RESPONSE.format(
        user_email=user_email,
        response_id=response_id
    )

    query_result = db.execute(statement=sql_user_role_survey_resp).fetchone()

    if query_result[0] == 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not Authorized",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(token: HTTPAuthorizationCredentials):
    payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    user_email = payload.get("user").get("email").lower()
    return user_email
