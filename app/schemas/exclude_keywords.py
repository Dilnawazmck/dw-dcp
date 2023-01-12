from typing import List

from pydantic import BaseModel


class ExcludeKeyword(BaseModel):
    survey_id: int
    user_id: int
    keyword: List

    class Config:
        orm_mode = True


class ExcludeKeywordOut(BaseModel):
    keyword: List

    class Config:
        orm_mode = True
