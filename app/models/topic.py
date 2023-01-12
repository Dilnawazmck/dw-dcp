from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import JSONB

from app.models.base import Base


class Topic(Base):
    name = Column(String(255))
    context = Column(JSONB)
