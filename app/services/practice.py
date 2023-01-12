from app.models.practice import Practice
from app.services.base_service import BaseService


class PracticeService(BaseService):
    __model__ = Practice

    @property
    def model_cls(self):
        """Returns a class of model which binds to the service"""
        return self.__model__


_practice = PracticeService()
