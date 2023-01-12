from pydantic import BaseModel


class Client(BaseModel):
    id: str
    name: str

    class Config:
        orm_mode = True
