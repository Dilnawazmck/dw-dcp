import pandas as pd

from app.db import raw_sqls
from app.models.practice import Practice
from app.services.response import _response
from app.tests.conftest import get_test_db_session


def test_get_survey_responses():
    db_Session = next(get_test_db_session())
    res = _response.get_survey_responses(
        survey_id="40d4",
        db=db_Session,
        filters=None,
        user_id=1,
        user_saved_comment_join_type="left join",
        order_by="practice",
        folder_name="",
    )
    assert res["total_comments"] >= 0
    assert isinstance(res["data"], list)
    x = [item["practice_similarity_score"] for item in res["data"]]
    assert sorted(x, reverse=True) == x


def test_get_model_names_by_id():
    db_Session = next(get_test_db_session())
    res = _response.get_model_names_by_id(Practice, [2, 3], db=db_Session)
    assert isinstance(res, str)


def test_filter_summary():
    db_Session = next(get_test_db_session())
    res = _response.filter_summary(
        list([("practice_id", "eq", "4,3")]),
        db=db_Session,
        survey_id="40d4",
        practice_name="OHI",
    )
    assert isinstance(res, list)


def test_create_export_filter_summary():
    db_Session = next(get_test_db_session())
    res_filtersummary = _response.filter_summary(
        list([("practice_id", "eq", "4,3")]),
        db=db_Session,
        survey_id="40d4",
        practice_name="OHI",
    )
    res = _response.create_export_filter_summary(res_filtersummary)
    assert isinstance(res, pd.DataFrame)


def test_export_custom_topic():
    db_Session = next(get_test_db_session())
    sql_result = raw_sqls.GET_RESPONSE_EXPORT_SQL.format(
        survey_id=1, filter_sql="", user_id=1
    )
    db_result = _response.execute_raw_sql(sql_result, db_Session)
    assert "custom_topic" in db_result[0]._fields


def test_reset_all_comments():
    db_Session = next(get_test_db_session())

    delete_query = raw_sqls.DELETE_ALL_SAVED_COMMENTS.format(survey_id=1,user_id=1,survey_type=1)
    delete_response_result = _response.execute_dml_raw_sql(delete_query,db=db_Session)
    saved_comment_query = raw_sqls.GET_SAVED_RESPONSE_EXPORT_SQL.format(survey_id=1,user_id=1,filter_sql='')

    saved_response_result = _response.execute_raw_sql(saved_comment_query, db_Session)
    assert len(saved_response_result) == 0
