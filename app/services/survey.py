from sqlalchemy.orm import Session

from app.models.survey import Survey
from app.services.base_service import BaseService
from app.utils.app_utils import _hash


class SurveyService(BaseService):
    __model__ = Survey

    @property
    def model_cls(self):
        """Returns a class of model which binds to the service"""
        return self.__model__

    def get_surveys_filter_by_client(self, client_id: str, db: Session):
        decoded_client_id = _hash.decode(client_id)
        if not decoded_client_id:
            return []
        return (
            db.query(self.model_cls)
            .filter(self.model_cls.client_id == _hash.decode(client_id))
            .all()
        )


_survey = SurveyService()
