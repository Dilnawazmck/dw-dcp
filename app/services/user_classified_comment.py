from sqlalchemy.orm import Session

from app.models.user_classified_comment import UserClassifiedComment
from app.services.base_service import BaseService


class UserClassifiedCommentService(BaseService):
    __model__ = UserClassifiedComment

    @property
    def model_cls(self):
        """Returns a class of model which binds to the service"""
        return self.__model__

    def get_by_user_id_response_id(self, user_id: int, response_id: int, db: Session):
        return (
            db.query(self.model_cls)
            .filter(
                self.model_cls.user_id == user_id,
                self.model_cls.response_id == response_id,
            )
            .first()
        )


_user_classified_comment = UserClassifiedCommentService()
