from app.models.topic import Topic
from app.services.base_service import BaseService


class TopicService(BaseService):
    __model__ = Topic

    @property
    def model_cls(self):
        """Returns a class of model which binds to the service"""
        return self.__model__


_topic = TopicService()
