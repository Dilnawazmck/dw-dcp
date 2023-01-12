from sqlalchemy.orm import Session

from app.db import raw_sqls
from app.models.user import User
from app.services.base_service import BaseService
from app.services.role import _role
from app.utils.app_utils import _hash
from app.utils.constants import ADMIN, SUPER_ADMIN
from app.utils.dict_utils import safe_get


class UserService(BaseService):
    __model__ = User

    @property
    def model_cls(self):
        """Returns a class of model which binds to the service"""
        return self.__model__

    @staticmethod
    def hash_serialize_response(response):
        for cl in response:
            cl["id"] = _hash.encode(cl["id"])
            for survey in safe_get(cl, "surveys", []):
                survey["id"] = _hash.encode(survey["id"])
        return response

    @staticmethod
    def is_authorized(current_role_id: int, db: Session):
        user_role = _role.get_by_id(current_role_id, db)
        if user_role.name.lower() == ADMIN or user_role.name.lower() == SUPER_ADMIN:
            return True
        return False

    @staticmethod
    def is_allowed(current_role_id: int, update_role_id: int, db: Session):
        current_user_role = _role.get_by_id(current_role_id, db)
        update_user_role = _role.get_by_id(update_role_id, db)
        if (
            current_user_role.name.lower() == ADMIN
            and update_user_role.name.lower() == SUPER_ADMIN
        ):
            return False
        return True

    @staticmethod
    def get_roles(db: Session):
        return _role.get_all(db)

    def get_by_email(self, user_email: str, db: Session) -> User:
        return (
            db.query(self.model_cls)
            .filter(
                self.model_cls.email == user_email.lower(),
                self.model_cls.is_deleted.is_(False),
            )
            .first()
        )

    def get_by_id(self, user_id: str, db: Session) -> User:
        decoded_user_id = _hash.decode(user_id)
        if not decoded_user_id:
            return None

        return (
            db.query(self.model_cls)
            .filter(self.model_cls.id == decoded_user_id[0])
            .first()
        )

    def get_users(self, db: Session):
        sql_users = raw_sqls.GET_USERS
        response = self.execute_raw_sql(sql_users, db)
        response = [dict(row) for row in response]
        return self.hash_serialize_response(response)

    def get_user_details(self, user_id: str, db: Session):
        decoded_user_id = _hash.decode(user_id)
        if not decoded_user_id:
            return []

        user_result = (
            db.query(self.model_cls)
            .filter(self.model_cls.id == decoded_user_id[0])
            .first()
        )

        sql_users_survey = raw_sqls.GET_USER_SURVEY_SQL.format(
            user_id=decoded_user_id[0]
        )
        user_survey_result = self.execute_raw_sql(sql_users_survey, db)
        user_survey_result = [dict(row) for row in user_survey_result]
        self.hash_serialize_response(user_survey_result)

        response = {}
        response["full_name"] = user_result.full_name
        response["email"] = user_result.email
        response["role_name"] = user_result.role.name
        response["client_data"] = user_survey_result

        return response


_user = UserService()
