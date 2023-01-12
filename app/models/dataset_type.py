from sqlalchemy import Column, String

from app.models.base import Base


class DatasetType(Base):
    __tablename__ = "dataset_type"

    name = Column(String(255))
