from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session


from app.db.session import get_db_session
from app.services import authentication
from app.services.client import _client
from app.services.user import _user


router = APIRouter()


@router.get("/")
async def client_list(
    token: HTTPAuthorizationCredentials = Depends(authentication.verify_token),
    db: Session = Depends(get_db_session),
):
    user_email = authentication.get_current_user(token)
    user_obj = _user.get_by_email(user_email=user_email, db=db)

    response = _client.get_clients_and_surveys(user_obj, db)
    return response
