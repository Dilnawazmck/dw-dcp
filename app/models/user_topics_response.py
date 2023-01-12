from sqlalchemy import Column, String, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.models.base import Base


class UserTopicsResponse(Base):
    __tablename__ = "user_topics_response"

    response_id = Column(Integer, ForeignKey("response.id"), index=True, nullable=False)
    response = relationship("Response")

    user_id = Column(Integer, ForeignKey("user.id"), index=True, nullable=False)
    user = relationship("User")

    user_topic_id = Column(Integer, ForeignKey("user_topics.id"), index=True, nullable=False)
    user_topics = relationship("UserTopics")

    topic = Column(String(255))

    topic_similarity_score = Column(Float, index=True)
