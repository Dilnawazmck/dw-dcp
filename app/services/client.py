from sqlalchemy.orm import Session

from app.db import raw_sqls
from app.models.client import Client
from app.services.base_service import BaseService
from app.utils.app_utils import _hash
from app.utils.dict_utils import safe_get
from app.utils.constants import ADMIN, SUPER_ADMIN
from app.models.user import User


class ClientService(BaseService):
    __model__ = Client

    @property
    def model_cls(self):
        """Returns a class of model which binds to the service"""
        return self.__model__

    def get_clients_and_surveys(self, user_obj: User, db: Session):
        if user_obj.role.name.lower() == ADMIN or user_obj.role.name.lower() == SUPER_ADMIN:
            sql = raw_sqls.GET_CLIENTS_AND_SURVEYS_SQL
        else:
            sql = raw_sqls.GET_USER_SURVEY_SQL.format(
                user_id=user_obj.id
            )
        response = self.execute_raw_sql(sql, db)
        response = [dict(row) for row in response]

        return self.hash_serialize_response(response)

    @staticmethod
    def hash_serialize_response(response):
        for cl in response:
            cl["id"] = _hash.encode(cl["id"])
            for survey in safe_get(cl, "surveys", []):
                survey["id"] = _hash.encode(survey["id"])
        return response


_client = ClientService()
