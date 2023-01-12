from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class Role(Base):
    name = Column(String(255))
