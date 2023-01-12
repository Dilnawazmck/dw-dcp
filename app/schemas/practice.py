from pydantic import BaseModel


class Practice(BaseModel):
    id: int
    name: str
    outcome_name: str
    rank_id: int

    class Config:
        orm_mode = True
