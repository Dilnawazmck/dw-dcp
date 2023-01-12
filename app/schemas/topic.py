from pydantic import BaseModel


class Topic(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
