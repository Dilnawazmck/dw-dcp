from sqlalchemy import Boolean, Column, Enum, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class UserSavedComment(Base):
    __tablename__ = "user_saved_comment"
    user_id = Column(Integer, ForeignKey("user.id"), index=True, nullable=False)
    user = relationship("User")
    response_id = Column(Integer, ForeignKey("response.id"), nullable=False)
    response = relationship("Response")
    folder_name = Column(String(200), default="Default")
    __table_args__ = (
        Index("ix_user_saved_comment_user_id_response_id", "user_id", "response_id"),
    )
