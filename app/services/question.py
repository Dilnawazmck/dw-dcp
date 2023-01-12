from sqlalchemy.orm import Session

from app.models.question import Question
from app.services.base_service import BaseService
from app.utils.app_utils import _hash


class QuestionService(BaseService):
    __model__ = Question

    @property
    def model_cls(self):
        """Returns a class of model which binds to the service"""
        return self.__model__

    def get_survey_questions(self, survey_id: int, survey_type: int, db: Session):
        decoded_survey_id = _hash.decode(survey_id)
        if not decoded_survey_id:
            return None
        return (
            db.query(self.model_cls)
            .filter(
                self.model_cls.survey_id == decoded_survey_id[0],
                self.model_cls.type == survey_type,
            )
            .all()
        )


_question = QuestionService()
