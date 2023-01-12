from typing import List

from sqlalchemy.orm import Session

from app.db import raw_sqls
from app.models import Exclude_keywords
from app.services.base_service import BaseService
from app.utils.app_utils import _hash


class ExcludeKeywords(BaseService):
    __model__ = Exclude_keywords

    @property
    def model_cls(self):
        """Returns a class of model which binds to the service"""
        return self.__model__

    def get_exclude_keywords(self, survey_id: int, user_id: int, db: Session):
        return (
            db.query(self.model_cls)
            .filter(
                self.model_cls.survey_id == survey_id,
                self.model_cls.user_id == user_id,
            )
            .first()
        )

    def update_exclude_keyword(
        self, survey_id: int, user_id: int, exclude_keyword: List, db: Session
    ):
        if not survey_id:
            return []

        sql = raw_sqls.UPDATE_EXCLUDE_KEYWORDS.format(
            user_id=user_id, survey_id=survey_id, exclude_keyword=exclude_keyword, db=db
        )
        self.execute_dml_raw_sql(sql, db)


_exclude_keywords = ExcludeKeywords()
