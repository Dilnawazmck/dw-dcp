from pydantic import BaseModel


class TextClassificationSchema(BaseModel):
    text: list
    labels: list
