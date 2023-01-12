from sqlalchemy import Column, String

from app.models.base import Base


class FeedbackCategory(Base):
    __tablename__ = "feedback_category"
    name = Column(String(500))
