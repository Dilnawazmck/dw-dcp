from sqlalchemy.orm import Session

from app.db import raw_sqls
from app.models.response import Response
from app.models.user_saved_comment import UserSavedComment
from app.services.base_service import BaseService
from app.services.user import _user
from app.utils.app_utils import _hash
from app.utils.constants import FolderUpperCap


class UserSavedCommentService(BaseService):
    __model__ = UserSavedComment

    @property
    def model_cls(self):
        """Returns a class of model which binds to the service"""
        return self.__model__

    def get_by_user_id_and_response_id(
        self, user_id: int, response_id: int, db: Session
    ) -> UserSavedComment:
        return (
            db.query(self.model_cls)
            .filter(
                self.model_cls.user_id == user_id,
                self.model_cls.response_id == response_id,
            )
            .first()
        )

    def get_survey_id_survey_type(self, response_id: int, db: Session) -> Response:
        return (
            db.query(Response.survey_id, Response.type)
            .filter(Response.id == response_id)
            .first()
        )

    def get_by_user_folder_list(
        self, user_id: int, survey_id: str, survey_type: int, db: Session
    ):
        decoded_survey_id = _hash.decode(survey_id)

        if not decoded_survey_id:
            return None

        sql_response = raw_sqls.GET_USER_SURVEY_FOLDER_LIST.format(
            survey_id=decoded_survey_id[0], user_id=user_id, survey_type=survey_type
        )
        db_result = self.execute_raw_sql(sql_response, db)
        if not db_result:
            return None

        folder_len = len(db_result)
        if folder_len <= FolderUpperCap:
            status = True
        else:
            status = False

        return {
            "data": db_result,
            "upper_cap_reached": status,
            "Total_folders": folder_len,
        }

    def remove_by_user_id_and_response_id(
        self, user_id: int, response_id: int, db: Session
    ):
        obj = self.get_by_user_id_and_response_id(
            user_id=user_id, response_id=response_id, db=db
        )
        db.delete(obj)
        db.commit()

    def remove_by_user_id_and_survey_id(
        self, user_id: int, db: Session, survey_id: int
    ):
        obj = self.get_by_user_id_and_response_id(
            user_id=user_id, survey_id=survey_id, db=db
        )
        db.delete(obj)
        db.commit()

    def remove_comments_by_user_id_survey_id(
        self, user_id: int, db: Session, survey_id: str,survey_type: int
    ):
        decoded_survey_id = _hash.decode(survey_id)
        if not decoded_survey_id:
            return None

        query = raw_sqls.DELETE_ALL_SAVED_COMMENTS.format(survey_id=decoded_survey_id[0],user_id=user_id, survey_type=survey_type)
        self.execute_dml_raw_sql(query,db)

_user_saved_comment = UserSavedCommentService()
