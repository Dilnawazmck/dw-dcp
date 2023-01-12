from pydantic import BaseModel


class Survey(BaseModel):
    id: str
    name: str
    filters: dict

    class Config:
        orm_mode = True


class SurveyQuestions(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
