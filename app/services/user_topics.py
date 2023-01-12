from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db import raw_sqls
from app.models.user_topics import UserTopics
from app.schemas import user_topics
from app.services.base_service import BaseService
from app.services.response import _response
from app.utils.app_utils import _hash
from app.utils.dict_utils import safe_get
from app.utils.list_utils import count_key
from app.utils.constants import UserTopicsType, UNCLASSIFIED_CATEGORY


class UserTopicsService(BaseService):
    __model__ = UserTopics

    @property
    def model_cls(self):
        """Returns a class of model which binds to the service"""
        return self.__model__

    @staticmethod
    def is_valid_topic_list(topic_list: list):
        if not (count_key("name", topic_list) > 0 and count_key("name", topic_list) == len(topic_list)):
            return None

        if not (count_key("type", topic_list) > 0 and count_key("type", topic_list) == len(topic_list)):
            return None

        for d in topic_list:
            topic_type = safe_get(d, "type")
            if topic_type not in [UserTopicsType.PRACTICE.value, UserTopicsType.STANDARD.value,
                                  UserTopicsType.CUSTOM.value]:
                return None

        return True

    def get_user_topics_by_user_id_and_survey_id(self, user_id: int, survey_id: str, db: Session) -> UserTopics:
        decoded_survey_id = _hash.decode(survey_id)
        if not decoded_survey_id:
            return None

        user_topic_obj = db.query(self.model_cls).filter(
            self.model_cls.user_id == user_id,
            self.model_cls.survey_id == decoded_survey_id[0]
        ).first()

        return user_topic_obj

    def get_sentiment_counts_by_user_topic(self,user_id: int, survey_id: str, filters:str,db: Session):
        decoded_survey_id = _hash.decode(survey_id)
        if not decoded_survey_id:
            return None

        parsed_filters = _response.parse_filters(filters)
        filter_sql, _, _ = _response.add_filters(parsed_filters)
        sql = raw_sqls.GET_SENTIMENT_COUNT_BY_USER_TOPIC.format(
            user_id=user_id,
            survey_id=decoded_survey_id[0],
            filter_sql=filter_sql,
            sentiment_id='{"sentiment_id":',
            sentiment_name=r',"name":"',
            sentiment_count=r'","count":',
            end_string=r'}',
        )
        response = self.execute_raw_sql(sql, db)
        return response


    def create_user_topic_list(self, user_id: int, survey_id: str, topics_list: list, db: Session) -> UserTopics:
        # check if topic list is valid
        if not self.is_valid_topic_list(topic_list=topics_list):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not a Valid topic list"
            )
        # check if entry already exist
        user_topics_obj = self.get_user_topics_by_user_id_and_survey_id(user_id, survey_id, db)
        if user_topics_obj:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Entry already exists"
            )

        # create user topic list
        decoded_survey_id = _hash.decode(survey_id)
        topics_list.append({"name": UNCLASSIFIED_CATEGORY, "type": UserTopicsType.STANDARD.value})
        user_topics_obj_in = user_topics.AddUserTopics(
            user_id=user_id,
            topics=topics_list,
            survey_id=decoded_survey_id[0]
        )
        response = self.create(db=db, obj_in=user_topics_obj_in)
        return response

    def update_user_topics(self, user_topics_obj: UserTopics, topics_list: list, db: Session):
        # check if topic list is valid
        if not self.is_valid_topic_list(topic_list=topics_list):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not a Valid topic list"
            )

        topics_list.append({"name": UNCLASSIFIED_CATEGORY, "type": UserTopicsType.STANDARD.value})
        update_dict = {"topics": topics_list}
        self.update(db_obj=user_topics_obj, update_data=update_dict, db=db)

    def get_counts_in_survey_user_topics(
        self, user_id: int, survey_id: str, filters: str, db: Session
    ):
        decoded_survey_id = _hash.decode(survey_id)
        if not decoded_survey_id:
            return []

        parsed_filters = _response.parse_filters(filters)
        filter_sql, _, _ = _response.add_filters(parsed_filters)
        sql = raw_sqls.GET_COMMENTS_COUNT_PER_USER_TOPIC_GROUP_SQL.format(
            user_id=user_id,
            survey_id=decoded_survey_id[0],
            filter_sql=filter_sql,
        )
        return self.execute_raw_sql(sql, db)

    def get_popular_words_in_survey_by_user_topics(
            self, user_id: int, survey_id: str, filters: str, db: Session
    ):
        decoded_survey_id = _hash.decode(survey_id)
        if not decoded_survey_id:
            return []

        parsed_filters = _response.parse_filters(filters)
        filter_sql, exclude_sql, _ = _response.add_filters(parsed_filters)
        sql = raw_sqls.GET_TOP_WORDS_IN_SURVEY_BY_USER_TOPICS_SQL.format(
            user_id=user_id,
            survey_id=decoded_survey_id[0],
            top_n=10,
            filter_sql=filter_sql,
            exclude_sql=exclude_sql,
        )
        resp = self.execute_raw_sql(sql, db)
        return resp

    def get_survey_responses_with_topics(
        self,
        survey_id: str,
        db: Session,
        filters: str,
        user_id: int,
        user_saved_comment_join_type: str,
        skip: int = 0,
        limit: int = 10,
    ):
        decoded_survey_id = _hash.decode(survey_id)
        if not decoded_survey_id:
            return {"total_comments": 0, "data": []}

        parsed_filters = _response.parse_filters(filters)
        filter_sql, _, user_saved_comment_join = _response.add_filters(parsed_filters)
        total_comments_sql = raw_sqls.GET_TOTAL_COMMENTS_WITH_FILTER.format(
            survey_id=decoded_survey_id[0],
            filter_sql=filter_sql,
            user_saved_comment_join=user_saved_comment_join,
        )
        sql = raw_sqls.GET_SURVEY_RESPONSES_WITH_USER_TOPICS.format(
            survey_id=decoded_survey_id[0],
            filter_sql=filter_sql,
            user_id=user_id,
            user_saved_comment_join_type=user_saved_comment_join_type,
            limit=limit,
            offset=skip,
        )
        total_comments = self.execute_raw_sql(total_comments_sql, db)
        db_result = self.execute_raw_sql(sql, db)

        # Update demographics dict with actual key value
        response = _response.transform_response_with_updated_demographics(
            decoded_survey_id[0], db_result, db
        )

        return {"total_comments": total_comments[0].count, "data": response}


_user_topics = UserTopicsService()
