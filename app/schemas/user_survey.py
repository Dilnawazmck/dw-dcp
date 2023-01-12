from pydantic import BaseModel
from typing import List


class AddUserSurveyIn(BaseModel):
    user_id: str
    survey_id: List


class AddUserSurvey(BaseModel):
    user_id: int
    survey_id: int

    class Config:
        orm_mode = True


class DeleteUserSurveyIn(BaseModel):
    user_id: str
    survey_id: List
    is_delete: bool
