from sqlalchemy import Column, ForeignKey, Index, Integer
from sqlalchemy.orm import relationship

from app.models.base import Base


class UserClassifiedComment(Base):
    __tablename__ = "user_classified_comment"
    user_id = Column(Integer, ForeignKey("user.id"), index=True, nullable=False)
    user = relationship("User")
    response_id = Column(Integer, ForeignKey("response.id"), nullable=False)
    response = relationship("Response")
    __table_args__ = (
        Index(
            "ix_user_classified_comment_user_id_response_id", "user_id", "response_id"
        ),
    )
