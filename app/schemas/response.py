from typing import Any, Optional

from pydantic import BaseModel


class ReclassifyIn(BaseModel):
    response_id: int
    topic_id: Optional[int]
    practice_id: Optional[int]
    sentiment_id: Optional[int]

    class Config:
        orm_mode = True


class ReclassifyOut(BaseModel):
    id: int
    topic_id: int
    practice_id: int
    question_id: int
    answer: str
    answer_lang: str
    translated_en_answer: Optional[str]
    sentiment_id: int

    class Config:
        orm_mode = True
