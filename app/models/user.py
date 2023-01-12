from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class User(Base):
    full_name = Column(String(255))
    email = Column(String(255), unique=True, index=True, nullable=False)
    is_active = Column(Boolean(), default=True)
    role_id = Column(Integer, ForeignKey("role.id"))
    role = relationship("Role")
    # items = relationship("Item", back_populates="owner")
