from pydantic import BaseModel
from typing import Optional


class AddUserIn(BaseModel):
    email: str
    full_name: str
    role_id: int


class EditUserIn(BaseModel):
    id: str
    email: Optional[str]
    full_name: Optional[str]
    role_id: Optional[int]


class AddUser(BaseModel):
    email: str
    full_name: str
    role_id: int

    class Config:
        orm_mode = True


class AddUserOut(BaseModel):
    email: str
    full_name: str
    role_id: int

    class Config:
        orm_mode = True
