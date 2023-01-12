from sqlalchemy import Column, Integer, ForeignKey


from app.models.base import Base


class UserSurvey(Base):
    __tablename__ = "user_survey"
    user_id = Column(Integer, ForeignKey("user.id"),  nullable=False)
    survey_id = Column(Integer, ForeignKey("survey.id"), nullable=False)
