import mock
import pytest
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from app.core import config
from app.models import *
from app.models import Base

# from testcontainers.postgres import PostgresContainer


security = HTTPBearer()


@pytest.fixture(scope="session", autouse=True)
def db_setup(request):
    # print("\nIn db_setup()")
    # cont = PostgresContainer()
    # cont.start()
    mock.patch(
        "app.core.config.SQLALCHEMY_DATABASE_URI",
        config.TEST_DATABASE_URI,
    ).start()
    engine = create_engine(config.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
    Base.metadata.create_all(bind=engine)

    client_data = {"id": 1, "name": "TestClient1"}

    survey_data = {
        "id": 1,
        "name": "TestSurvey1",
        "filters": '{"demo_BU": { \
        "options": [{"column_value": "BU_1", "display_name": "Business Unit 1"}, \
                    {"column_value": "BU_2", "display_name": "Business Unit 2"}], "display_name": "Company"}}',
        "client_id": 1,
        "type": 1,
    }
    response_data1 = {
        "id": 1,
        "question_id": 1,
        "answer": "Please see above.",
        "answer_lang": "en",
        "topic_id": 1,
        "practice_id": 1,
        "top_words": '{"see": 1,"please": 1}',
        "survey_id": "1",
        "sentiment_id": "1",
        "sentiment_score": ".4",
        "confirmit_resp_id": "32",
        "topic_similarity_score": ".80",
        "practice_similarity_score": ".50",
        "type": 1,
        "filter_json": '{"demo_BU": "BU_1","demo_Line": "Line_14","demo_Type": "Type_6","demo_State":"State_22","demo_Gender":"Gender_4","demo_Tenure":"Tenure_6","demo_Country": "Country_1","demo_OHIPart": "OHIPart_1","demo_Location": "Location_165","demo_Ethnicity": "Ethnicity_7","demo_Workstream": "Workstream_9", "demo_Transformation": "Transformation_1"}',
    }

    response_data2 = {
        "id": 2,
        "question_id": 1,
        "answer": "Please see above.",
        "answer_lang": "en",
        "topic_id": 1,
        "practice_id": 1,
        "top_words": '{"see": 1,"please": 1}',
        "survey_id": "1",
        "sentiment_id": "2",
        "sentiment_score": ".1",
        "confirmit_resp_id": "32",
        "topic_similarity_score": ".10",
        "practice_similarity_score": ".40",
        "type": 1,
        "filter_json": '{"demo_BU": "BU_1","demo_Line": "Line_14","demo_Type": "Type_6","demo_State":"State_22","demo_Gender":"Gender_4","demo_Tenure":"Tenure_6","demo_Country": "Country_1","demo_OHIPart": "OHIPart_1","demo_Location": "Location_165","demo_Ethnicity": "Ethnicity_7","demo_Workstream": "Workstream_9", "demo_Transformation": "Transformation_1"}',
    }

    response_data3 = {
        "id": 3,
        "question_id": 1,
        "answer": "Please see above.",
        "answer_lang": "en",
        "topic_id": 1,
        "practice_id": 1,
        "top_words": '{"see": 1,"please": 1}',
        "survey_id": "1",
        "sentiment_id": "3",
        "sentiment_score": ".9",
        "confirmit_resp_id": "32",
        "topic_similarity_score": ".90",
        "practice_similarity_score": ".90",
        "type": 1,
        "filter_json": '{"demo_BU": "BU_1","demo_Line": "Line_14","demo_Type": "Type_6","demo_State":"State_22","demo_Gender":"Gender_4","demo_Tenure":"Tenure_6","demo_Country": "Country_1","demo_OHIPart": "OHIPart_1","demo_Location": "Location_165","demo_Ethnicity": "Ethnicity_7","demo_Workstream": "Workstream_9", "demo_Transformation": "Transformation_1"}',
    }

    question_data = {
        "id": 1,
        "name": "Describe Company in three words.",
        "survey_id": 1,
        "type": 1,
    }

    role_data = {"id": 1, "name": "user"}

    topic_data = {"id": 1, "name": "test topic"}

    practice_data = {
        "id": 1,
        "name": "test practice",
        "outcome_name": "test outcome",
        "rank_id": 1,
        "type": 1,
    }

    user_data = {
        "id": 1,
        "full_name": "test",
        "email": "test@test.com",
        "is_active": True,
        "role_id": 1,
    }
    user_survey = {
        "id": 1,
        "user_id": 1,
        "survey_id": 1,
    }

    user_survey_preset = {
        "id": 1,
        "is_deleted": False,
        "name": "ABC",
        "preset_filters": '[{"name": "standard"}]',
        "survey_id": 1,
        "user_id": 1,
    }

    user_topic_data = {
        "id": 1,
        "user_id": 1,
        "topics": '[{"name": "test topic", "type": "custom"}]',
        "survey_id": 1,
    }

    custom_topics_job = {
        "id": 1,
        "user_topic_id": 1,
        "survey_id": 1,
        "status": "queue",
        "action": "create",
    }

    sentiment_data_1 = {"id": 1, "is_deleted": False, "name": "Neutral"}
    sentiment_data_2 = {"id": 2, "is_deleted": False, "name": "Positive"}
    sentiment_data_3 = {"id": 3, "is_deleted": False, "name": "Negative"}

    with engine.connect() as con:
        delete_response = text(
            """
            Delete from response
        """
        )
        delete_question = text(
            """
            Delete from question
        """
        )
        delete_user_survey_preset = text(
            """
            Delete from user_survey_preset
        """
        )
        delete_user_survey = text(
            """
        Delete from user_survey
        """
        )
        delete_client = text(
            """
        Delete from client
        """
        )
        delete_survey = text(
            """
        Delete from survey
        """
        )
        delete_role = text(
            """
        Delete from role
        """
        )
        delete_user = text(
            """
        Delete from public.user
        """
        )
        delete_user_modal = text(
            """
            Delete from user_modal
        """
        )
        delete_user_topics = text(
            """
            Delete from user_topics
        """
        )
        delete_custom_topics_job = text(
            """
            Delete from custom_topics_job
        """
        )
        delete_topic = text(
            """
            Delete from topic
        """
        )
        delete_practice = text(
            """
            Delete from practice
        """
        )
        delete_sentiment = text(
            """
            Delete from sentiment
            """
        )

        delete_user_saved_comment = text(""" Delete from user_saved_comment""")

        practice_statement = text(
            """
        INSERT into practice(id, last_updated_on, created_on, is_deleted, name, outcome_name, rank_id)
        VALUES(:id, now(), now(), False, :name, :outcome_name, :rank_id)
        """
        )

        sentiment_statement = text(
            """
            INSERT into sentiment(id, last_updated_on, created_on, is_deleted, name)
            VALUES (:id, now(),now(),:is_deleted,:name)
            """
        )

        topic_statement = text(
            """
        INSERT into topic(id, last_updated_on, created_on, is_deleted, name)
        VALUES(:id, now(), now(), False, :name)
        """
        )
        user_survey_preset_statement = text(
            """
            INSERT into user_survey_preset
            (id, last_updated_on, created_on, is_deleted, user_id, preset_filters, survey_id, name)
            VALUES
            (:id,now(),now(),:is_deleted,:user_id,:preset_filters,:survey_id,:name)
            """
        )

        client_statement = text(
            """
        INSERT into client(id, last_updated_on, created_on, is_deleted, name)
        VALUES(:id, now(), now(), False, :name)
        """
        )

        survey_statement = text(
            """
        INSERT into survey(id, last_updated_on, created_on, is_deleted, name, filters, client_id, type)
        VALUES(:id, now(), now(), False, :name, :filters, :client_id, :type)
        """
        )

        response_data_statement = text(
            """
            INSERT INTO public."response"(id, last_updated_on, created_on, is_deleted, question_id, answer, answer_lang,
            topic_id,  practice_id,  top_words, filter_json, survey_id, confirmit_resp_id,topic_similarity_score, practice_similarity_score,sentiment_id,sentiment_score,type)
            VALUES(:id,now(),now(),False,:question_id,:answer,:answer_lang,:topic_id,:practice_id,:top_words,:filter_json,:survey_id,:confirmit_resp_id,:topic_similarity_score,:practice_similarity_score,:sentiment_id,:sentiment_score,:type)
        """
        )

        question_data_statement = text(
            """
            INSERT INTO public."question"(id, last_updated_on, created_on, is_deleted, name, survey_id)
            VALUES (:id,now(),now(),False,:name,:survey_id)
         """
        )

        role_statement = text(
            """
        INSERT into role(id, last_updated_on, created_on, is_deleted, name)
        VALUES(:id, now(), now(), False, :name)
        """
        )

        user_statement = text(
            """
        INSERT into public."user"(id, last_updated_on, created_on, is_deleted, full_name, email, is_active, role_id)
        VALUES(:id, now(), now(), False, :full_name, :email, :is_active, :role_id)
        """
        )

        user_survey_statement = text(
            """
        INSERT into public."user_survey"(id, last_updated_on, created_on, is_deleted, user_id, survey_id)
        VALUES(:id, now(), now(), False, :user_id, :survey_id)
        """
        )

        user_topics_statement = text(
            """
        INSERT into public."user_topics"(id, last_updated_on, created_on, is_deleted, user_id, topics, survey_id)
        VALUES(:id, now(), now(), False, :user_id, :topics, :survey_id)
        """
        )

        custom_topics_job_statement = text(
            """
        INSERT into public."custom_topics_job"(id, last_updated_on, created_on, is_deleted, user_topic_id, survey_id, status, action)
        VALUES(:id, now(), now(), False, :user_topic_id, :survey_id, :status, :action)
        """
        )

        con.execute(delete_custom_topics_job)
        con.execute(delete_user_topics)
        con.execute(delete_user_survey_preset)
        con.execute(delete_user_saved_comment)
        con.execute(delete_response)
        con.execute(delete_question)
        con.execute(delete_user_survey)
        con.execute(delete_survey)
        con.execute(delete_user_modal)
        con.execute(delete_user)
        con.execute(delete_client)
        con.execute(delete_role)
        con.execute(delete_topic)
        con.execute(delete_practice)
        con.execute(delete_sentiment)

        con.execute(topic_statement, **topic_data)
        con.execute(practice_statement, **practice_data)
        con.execute(client_statement, **client_data)
        con.execute(survey_statement, **survey_data)
        con.execute(role_statement, **role_data)
        con.execute(user_statement, **user_data)
        con.execute(user_survey_statement, **user_survey)
        con.execute(question_data_statement, **question_data)
        con.execute(response_data_statement, **response_data1)
        con.execute(response_data_statement, **response_data2)
        con.execute(response_data_statement, **response_data3)
        con.execute(user_survey_preset_statement, **user_survey_preset)
        con.execute(user_topics_statement, **user_topic_data)
        con.execute(custom_topics_job_statement, **custom_topics_job)
        con.execute(sentiment_statement, **sentiment_data_1)
        con.execute(sentiment_statement, **sentiment_data_2)
        con.execute(sentiment_statement, **sentiment_data_3)

    # def db_teardown():
    #     print("In my_own_session_run_at_end()")
    #     cont.stop()
    #
    # request.addfinalizer(db_teardown)


def get_test_db_session():
    engine = create_engine(config.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    try:
        db_session = session_local()
        yield db_session
    finally:
        db_session.close()


def override_verify_token(token: HTTPAuthorizationCredentials = Depends(security)):
    return token


def override_get_current_user(token: HTTPAuthorizationCredentials):
    return "test@test.com"


def override_verify_token_via_okta(
    token: HTTPAuthorizationCredentials = Depends(security),
):
    return token
