from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class CustomTopicsJob(Base):
    __tablename__ = "custom_topics_job"

    user_topic_id = Column(Integer, ForeignKey("user_topics.id"), index=True, nullable=False)
    user_topics = relationship("UserTopics")

    survey_id = Column(Integer, ForeignKey("survey.id"), index=True, nullable=False)
    survey = relationship("Survey")

    status = Column(String(100))
    action = Column(String(100))
