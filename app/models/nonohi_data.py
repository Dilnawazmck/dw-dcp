from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class Nonohi_Data(Base):
    __tablename__ = "nonohi_data"
    user_id = Column(Integer, ForeignKey("user.id"), index=True, nullable=False)
    user = relationship("User")
    client_name = Column(String(200), nullable=False)
    dataset_name = Column(String(200), nullable=False)
    dataset_type_id = Column(
        Integer, ForeignKey("dataset_type.id"), index=True, nullable=False
    )
    dataset_type = relationship("DatasetType")

    s3_path = Column(String(200))
    status = Column(String(200), nullable=False)
    pid = Column(String(200))
