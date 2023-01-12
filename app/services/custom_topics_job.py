import time, math
from fastapi import HTTPException, status
from sqlalchemy import or_, desc
from sqlalchemy.orm import Session

from app.models.custom_topics_job import CustomTopicsJob
from app.services.base_service import BaseService
from app.services.response import _response
from app.db import raw_sqls
from app.core.config import DATA_CHUNK_SIZE, CHUNK_PROCESSING_TIME
from app.utils.constants import CustomTopicsJobStatus
from app.utils.app_utils import _hash


class CustomTopicsJobService(BaseService):
    __model__ = CustomTopicsJob

    @property
    def model_cls(self):
        return self.__model__

    @staticmethod
    def get_time_in_hours_minutes(seconds: int):
        time_clause = []
        if not seconds and seconds <= 0:
            return None
        time_obj = time.gmtime(seconds)
        hrs = time_obj.tm_hour
        mins = time_obj.tm_min

        if hrs > 0:
            time_clause.append(f"{hrs} hours")
        if mins > 0:
            time_clause.append(f"{mins} minutes")
        else:
            time_clause.append(f"1 minute")

        return " ".join(time_clause)

    def get_latest_custom_topics_job_status(self, user_topic_id: int, db: Session):
        return (
            db.query(self.model_cls).filter(
                self.model_cls.user_topic_id == user_topic_id
            ).order_by(desc(self.model_cls.id)).first()
        )

    def get_custom_topic_job_by_topic_id(self, user_topic_id: int, db: Session) -> CustomTopicsJob:
        return (
            db.query(self.model_cls).filter(
                self.model_cls.user_topic_id == user_topic_id,
                or_(self.model_cls.status == CustomTopicsJobStatus.QUEUE.value,
                    self.model_cls.status == CustomTopicsJobStatus.PROCESSING.value)
            ).first()
        )

    def is_custom_topics_job_pending(self, user_topic_id: int, db: Session):
        custom_topics_job_obj = self.get_custom_topic_job_by_topic_id(user_topic_id=user_topic_id, db=db)

        if custom_topics_job_obj is not None and custom_topics_job_obj.status in [CustomTopicsJobStatus.QUEUE.value,
                                                                                  CustomTopicsJobStatus.PROCESSING.value]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job already in processing."
            )

    def get_job_completion_time(self, survey_id: str, db: Session):
        decoded_survey_id = _hash.decode(survey_id)
        if not decoded_survey_id:
            return None

        total_comments_sql = raw_sqls.GET_TOTAL_COMMENTS_WITH_FILTER.format(
            survey_id=decoded_survey_id[0],
            filter_sql="",
            user_saved_comment_join="",
        )

        total_comments = self.execute_raw_sql(total_comments_sql, db)
        if not total_comments:
            return None
        total_sec_to_complete = ((math.ceil(total_comments[0].count/DATA_CHUNK_SIZE) if total_comments[0].count > DATA_CHUNK_SIZE
                                 else 1) * CHUNK_PROCESSING_TIME) * 2

        return self.get_time_in_hours_minutes(total_sec_to_complete)


_custom_topics_job = CustomTopicsJobService()
