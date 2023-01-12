from pydantic import BaseModel
from typing import List


class AddUserTopics(BaseModel):
    user_id: int
    topics: List
    survey_id: int

    class Config:
        orm_mode = True


class GetUserTopics(BaseModel):
    topics: List

    class Config:
        orm_mode = True

