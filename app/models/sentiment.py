from sqlalchemy import Boolean, String, Integer, Column
from sqlalchemy.orm import relationship
from app.models.base import Base


class Sentiment(Base):
    name = Column(String(200))
