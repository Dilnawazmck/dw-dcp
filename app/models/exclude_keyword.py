from sqlalchemy import Column,ForeignKey,Integer,String,JSON
from sqlalchemy.orm import relationship
from app.models.base import Base
from sqlalchemy.dialects.postgresql import JSONB

class Exclude_keywords(Base):
    survey_id = Column(Integer, ForeignKey("survey.id"),index=True)
    survey = relationship("Survey")
    user_id = Column(Integer, ForeignKey("user.id"), index=True)
    user = relationship("User")
    keyword = Column(JSONB,index=True)
