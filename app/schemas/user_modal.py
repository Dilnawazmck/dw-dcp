from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import Boolean, Column, Integer


class UserModalIn(BaseModel):
    user_id: int
    show_modal: bool
    show_classify_modal: bool

    class Config:
        orm_mode = True


class UserModalOut(BaseModel):
    id: int
    show_modal: bool
    show_classify_modal: bool

    class Config:
        orm_mode = True
