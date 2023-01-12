from sqlalchemy.orm import Session

from app.db import raw_sqls
from app.models.user_modal import UserModal
from app.services.base_service import BaseService
from app.utils.app_utils import _hash


class UserModalServices(BaseService):
    __model__ = UserModal

    @property
    def model_cls(self):
        """Returns a class of model which binds to the service"""
        return self.__model__

    def get_user_modal_status(self, user_id: int, db: Session) -> UserModal:
        return (
            db.query(
                self.model_cls.show_modal,
                self.model_cls.show_classify_modal,
                self.model_cls.last_updated_on,
            )
            .filter(self.model_cls.user_id == user_id)
            .first()
        )

    def get_user_classification_comments(
        self,
        user_id: int,
        db: Session,
        survey_id: str,
        survey_type: int,
        length: int,
        total_limit: int,
    ):

        decoded_survey_id = _hash.decode(survey_id)
        if not decoded_survey_id:
            return []

        practice_type = 1 if survey_type == 4 else survey_type

        comments_sql = raw_sqls.GET_COMMENTS_TO_CLASSIFY.format(
            survey_id=decoded_survey_id[0],
            user_id=user_id,
            response_type=survey_type,
            practice_type=practice_type,
            length=length,
            total_limit=total_limit,
        )
        db_result = self.execute_raw_sql(comments_sql, db)
        return db_result

    def get_by_user_id(self, user_id: int, db: Session) -> UserModal:
        return (
            db.query(self.model_cls).filter(self.model_cls.user_id == user_id).first()
        )


_user_modal = UserModalServices()
