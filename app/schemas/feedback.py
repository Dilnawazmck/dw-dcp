from typing import Dict, List, Optional

from pydantic import BaseModel


class FeedbackCategory(BaseModel):
    id: str
    name: str

    class Config:
        orm_mode = True


class FeedbackCreate(BaseModel):
    response_id: int
    feedback_category_id: int
    description: str

    class Config:
        orm_mode = True
