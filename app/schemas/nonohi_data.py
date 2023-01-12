from pydantic import BaseModel


class NonohiData(BaseModel):
    user_id: int
    client_name: str
    dataset_name: str
    dataset_type_id: int
    status: str

    class Config:
        orm_mode = True


class NonohiDataOut(BaseModel):
    client_name: str
    dataset_name: str
    s3_path: str
    status: str

    class Config:
        orm_mode = True
