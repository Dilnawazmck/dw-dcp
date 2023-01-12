from pydantic import BaseModel

from app.utils.constants import DEFAULTFOLDER


class UserClassifyComment(BaseModel):
    user_id: int
    response_id: int

    class Config:
        orm_mode = True
