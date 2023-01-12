from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base


class Survey(Base):
    name = Column(String(255))
    filters = Column(JSONB)
    client_id = Column(Integer, ForeignKey("client.id"), index=True)
    client = relationship("Client")
    confirmit_pid = Column(String(255))
    type = Column(Integer, ForeignKey("dataset_type.id"), index=True, nullable=False)
    dataset_type = relationship("DatasetType")
