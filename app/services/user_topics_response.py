from app.models.user_topics_response import UserTopicsResponse
from app.services.base_service import BaseService


class UserTopicsResponseService(BaseService):
    __model__ = UserTopicsResponse

    @property
    def model_cls(self):
        """Returns a class of model which binds to the service"""
        return self.__model__


_user_topics_response = UserTopicsResponseService()