from pydantic import BaseModel
from app.utils.constants import DEFAULTFOLDER

class SaveCommentIn(BaseModel):
    response_id: int
    folder_name: str = DEFAULTFOLDER


class SaveComment(BaseModel):
    response_id: int
    user_id: int
    folder_name: str

    class Config:
        orm_mode = True


class SaveCommentOut(BaseModel):
    id: int
    response_id: int

    class Config:
        orm_mode = True
