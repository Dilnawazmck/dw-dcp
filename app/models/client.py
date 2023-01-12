from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import JSONB

from app.models.base import Base


class Client(Base):
    name = Column(String(255))
    topics = Column(JSONB)
    ohi_practices = Column(JSONB)
