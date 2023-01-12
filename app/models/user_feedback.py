from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class UserFeedback(Base):
    __tablename__ = "user_feedback"

    response_id = Column(Integer, ForeignKey("response.id"), index=True)
    response = relationship("Response")
    feedback_category_id = Column(
        Integer, ForeignKey("feedback_category.id"), index=True
    )
    feedback_category = relationship("FeedbackCategory")
    description = Column(String(50000))
