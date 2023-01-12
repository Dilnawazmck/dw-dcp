from pydantic import BaseModel


class AddCustomTopicsJob(BaseModel):
    user_topic_id: int
    survey_id: int
    status: str
    action: str

    class Config:
        orm_mode = True
