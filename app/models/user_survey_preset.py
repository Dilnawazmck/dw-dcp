from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base


class UserSurveyPreset(Base):
    __tablename__ = "user_survey_preset"
    user_id = Column(Integer, ForeignKey("user.id"), index=True, nullable=False)
    user = relationship("User")
    preset_filters = Column(JSONB)
    survey_id = Column(Integer, ForeignKey("survey.id"), index=True, nullable=False)
    survey = relationship("Survey")
    name = Column(String)
    type = Column(Integer, ForeignKey("dataset_type.id"), index=True, nullable=False)
    dataset_type = relationship("DatasetType")
