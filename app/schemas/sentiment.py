from pydantic import BaseModel


class Sentiment(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
