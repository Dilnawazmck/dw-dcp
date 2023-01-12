from sqlalchemy import Boolean, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.models.base import Base


class UserModal(Base):

    __tablename__ = "user_modal"
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, unique=True)
    user = relationship("User")
    show_modal = Column(Boolean, nullable=False)
    show_classify_modal = Column(Boolean, nullable=False)
