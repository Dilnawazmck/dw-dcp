from sqlalchemy.orm import Session

from app.models.user_feedback import UserFeedback
from app.services.base_service import BaseService


class UserFeedbackService(BaseService):
    __model__ = UserFeedback

    @property
    def model_cls(self):
        """Returns a class of model which binds to the service"""
        return self.__model__


_user_feedback = UserFeedbackService()
