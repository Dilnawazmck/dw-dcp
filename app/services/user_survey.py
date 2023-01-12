from sqlalchemy.orm import Session

from app.models.user_survey import UserSurvey
from app.services.base_service import BaseService
from app.utils.app_utils import _hash
from app.schemas.user_survey import AddUserSurveyIn, AddUserSurvey, DeleteUserSurveyIn


class UserSurveyService(BaseService):
    __model__ = UserSurvey

    @property
    def model_cls(self):
        """Returns a class of model which binds to the service"""
        return self.__model__

    def add_user_survey(self, data: AddUserSurveyIn, db: Session):
        decoded_user_id = _hash.decode(data.user_id)
        if not decoded_user_id:
            return None

        if len(data.survey_id) == 0:
            return None

        for item in data.survey_id:
            decoded_survey_id = _hash.decode(item)
            is_user_survey = db.query(self.model_cls).filter(
                self.model_cls.user_id == decoded_user_id[0],
                self.model_cls.survey_id == decoded_survey_id[0]
            ).first()

            obj_in = AddUserSurvey(
                user_id=decoded_user_id[0],
                survey_id=decoded_survey_id[0]
            )

            if not is_user_survey:
                self.create(obj_in=obj_in, db=db)

        return {"success": True}

    def remove_by_user_id_and_survey_id(self, data: DeleteUserSurveyIn, db: Session):
        decoded_user_id = _hash.decode(data.user_id)
        if not decoded_user_id:
            return None

        if len(data.survey_id) == 0:
            return None

        for item in data.survey_id:
            decoded_survey_id = _hash.decode(item)

            obj_del = db.query(self.model_cls).filter(
                self.model_cls.user_id == decoded_user_id[0],
                self.model_cls.survey_id == decoded_survey_id[0]).first()

            if obj_del:
                db.delete(obj_del)
                db.commit()


_user_survey = UserSurveyService()
