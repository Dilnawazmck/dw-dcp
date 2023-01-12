from pydantic import BaseModel
from typing import List



class UserSurveyPresetIn(BaseModel):
    preset_filters: List
    survey_id: int
    user_id: int
    name : str
    type : int

    class Config:
        orm_mode = True


