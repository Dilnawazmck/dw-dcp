import enum

from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base

SENTIMENT = [-1, 0, 1]  # -1: Negative 0:Neutral 1:Positive


class Response(Base):
    question_id = Column(Integer, ForeignKey("question.id"), index=True)
    question = relationship("Question")
    answer = Column(String(50000))
    answer_lang = Column(String(100))
    translated_en_answer = Column(String(50000))
    sentiment_id = Column(Integer, ForeignKey("sentiment.id"), index=True)
    sentiment = relationship("Sentiment")
    is_sentiment_verified = Column(Boolean, default=False)
    topic_id = Column(Integer, ForeignKey("topic.id"), index=True)
    topic = relationship("Topic")
    is_topic_verified = Column(Boolean, default=False)
    topic_similarity_score = Column(Float, index=True)
    practice_id = Column(Integer, ForeignKey("practice.id"), index=True)
    practice = relationship("Practice")
    is_practice_verified = Column(Boolean, default=False)
    practice_similarity_score = Column(Float, index=True)
    top_words = Column(JSONB, index=True)
    filter_json = Column(JSONB, index=True)
    survey_id = Column(Integer, ForeignKey("survey.id"), index=True)
    survey = relationship("Survey")
    confirmit_resp_id = Column(Integer)
    sentiment_score = Column(Float, index=True)
    type = Column(Integer, ForeignKey("dataset_type.id"), index=True, nullable=False)
    dataset_type = relationship("DatasetType")
