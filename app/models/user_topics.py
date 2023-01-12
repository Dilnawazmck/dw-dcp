from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base


class UserTopics(Base):
    __tablename__ = "user_topics"

    user_id = Column(Integer, ForeignKey("user.id"), index=True, nullable=False)
    user = relationship("User")

    topics = Column(JSONB)

    survey_id = Column(Integer, ForeignKey("survey.id"), index=True, nullable=False)
    survey = relationship("Survey")
