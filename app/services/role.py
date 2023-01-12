from sqlalchemy.orm import Session

from app.models.role import Role
from app.services.base_service import BaseService


class RoleService(BaseService):
    __model__ = Role

    @property
    def model_cls(self):
        """Returns a class of model which binds to the service"""
        return self.__model__


_role = RoleService()
