from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base


class Practice(Base):
    name = Column(String(255))
    context = Column(JSONB)
    outcome_name = Column(String(255))
    rank_id = Column(Integer)
    type = Column(Integer, ForeignKey("dataset_type.id"), index=True, nullable=False)
    dataset_type = relationship("DatasetType")
