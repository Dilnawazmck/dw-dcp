from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class Question(Base):
    name = Column(String(5000))
    type = Column(Integer)
    survey_id = Column(Integer, ForeignKey("survey.id"), index=True)
    survey = relationship("Survey")
