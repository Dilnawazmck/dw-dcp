from sqlalchemy.orm import Session

from app.models.feedback_category import FeedbackCategory
from app.services.base_service import BaseService


class FeedbackCategoryService(BaseService):
    __model__ = FeedbackCategory

    @property
    def model_cls(self):
        """Returns a class of model which binds to the service"""
        return self.__model__


_feedback_category = FeedbackCategoryService()