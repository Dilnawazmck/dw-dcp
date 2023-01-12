# import json
# import pandas as pd
#
# from sqlalchemy.orm import Session
#
# from app.services.data_ingestion import etl
# from app.tests.conftest import get_test_db_session
# from app.models.client import Client
# from app.models.survey import Survey
# from app.models.question import Question
# from app.models.response import Response
#
# test_data_file_path = [
#     "app/tests/test_data/data.csv",
#     "app/tests/test_data/metadata.json",
# ]
# test_project_id = "test_data"


# def test_etl():
#     db: Session = next(get_test_db_session())
#     conn = db.connection().connection
#
#     res_client_id = etl.insert_client_table(
#         connection=conn, data_file_path=test_data_file_path
#     )
#     assert res_client_id > 0
#     assert isinstance(res_client_id, int)
#     result_client_sql: Client = (
#         db.query(Client).filter(Client.id == res_client_id).first()
#     )
#     assert result_client_sql.name == "Test Company npn pset24june_15k"
#
#     res_survey_id = etl.insert_survey_table(
#         connection=conn,
#         project_id=test_project_id,
#         client_id=res_client_id,
#         data_file_path=test_data_file_path,
#     )
#     assert res_survey_id > 0
#     assert isinstance(res_survey_id, int)
#     result_survey_sql: Survey = (
#         db.query(Survey).filter(Survey.id == res_survey_id).first()
#     )
#     assert result_survey_sql.name == "Company_pset24june_15k_june_May2021"
#     assert result_survey_sql.confirmit_pid == test_project_id
#     assert result_survey_sql.client_id == res_client_id
#
#     etl.insert_question_table(
#         connection=conn, survey_id=res_survey_id, data_file_path=test_data_file_path
#     )
#
#     result_question_sql = (
#         db.query(Question).filter(Question.survey_id == res_survey_id).all()
#     )
#     assert isinstance(result_question_sql, list)
#     assert len(result_question_sql) == 5
#
#     etl.insert_response_table(
#         connection=conn,
#         db_session=db,
#         survey_id=res_survey_id,
#         data_file_path=test_data_file_path,
#     )
#
#     result_response_sql = (
#         db.query(Response).filter(Response.survey_id == res_survey_id).all()
#     )
#     assert isinstance(result_response_sql, list)
#     assert len(result_response_sql) == 23
#
#
# def test_read_csv_file():
#     result = etl.read_csv_file("app/tests/test_data/data.csv")
#
#     assert isinstance(result, pd.DataFrame)
#     assert len(result) == 6
#
#
# def test_read_json_file():
#     result = etl.read_json_file("app/tests/test_data/metadata.json")
#
#     assert isinstance(result, dict)
#     assert result["client_name"] == "Test Company npn pset24june_15k"
#     assert result["survey_name"] == "Company_pset24june_15k_june_May2021"
#     assert isinstance(result["data"], list)
#     assert isinstance(result["filters"], list)
#
#
# def test_list_to_dict():
#     test_list = [
#         {
#             "options": [{"column_value": "COMPANY_1", "display_name": "Company"}],
#             "column_name": "demo_COMPANY",
#             "display_name": "COMPANY",
#         },
#         {
#             "options": [
#                 {"column_value": "FUNCTION_1", "display_name": "Operations"},
#                 {"column_value": "FUNCTION_2", "display_name": "CEO"},
#                 {"column_value": "FUNCTION_3", "display_name": "Corporate Development"},
#                 {"column_value": "FUNCTION_4", "display_name": "Finance"},
#                 {"column_value": "FUNCTION_5", "display_name": "Human Resources"},
#                 {"column_value": "FUNCTION_6", "display_name": "Legal"},
#                 {"column_value": "FUNCTION_7", "display_name": "Major Projects"},
#             ],
#             "column_name": "demo_FUNCTION",
#             "display_name": "G FUNCTION",
#         },
#         {
#             "options": [
#                 {"column_value": "LOCATION_1", "display_name": "Canada"},
#                 {"column_value": "LOCATION_2", "display_name": "Mt Cattlin"},
#                 {"column_value": "LOCATION_3", "display_name": "Perth"},
#                 {"column_value": "LOCATION_4", "display_name": "Sal de Vida"},
#             ],
#             "column_name": "demo_LOCATION",
#             "display_name": "G LOCATION",
#         },
#         {
#             "options": [
#                 {"column_value": "JOBLEVEL_1", "display_name": "CEO"},
#                 {"column_value": "JOBLEVEL_2", "display_name": "Department Manager"},
#                 {"column_value": "JOBLEVEL_3", "display_name": "Executive"},
#                 {"column_value": "JOBLEVEL_4", "display_name": "General Manager"},
#                 {"column_value": "JOBLEVEL_5", "display_name": "Manager"},
#                 {"column_value": "JOBLEVEL_6", "display_name": "Senior Manager"},
#                 {
#                     "column_value": "JOBLEVEL_7",
#                     "display_name": "Senior Professional & Below",
#                 },
#                 {"column_value": "JOBLEVEL_8", "display_name": "Specialist"},
#                 {"column_value": "JOBLEVEL_9", "display_name": "Superintendent"},
#             ],
#             "column_name": "demo_JOBLEVEL",
#             "display_name": "G JOB LEVEL",
#         },
#         {
#             "options": [
#                 {"column_value": "StraightLiners_A", "display_name": "Yes"},
#                 {"column_value": "StraightLiners_B", "display_name": "No"},
#             ],
#             "column_name": "demo_StraightLiners",
#             "display_name": "Straight Liner / Speeder",
#         },
#     ]
#     result = etl.list_to_dict(test_list)
#     assert isinstance(result, str)
#     assert isinstance(json.loads(result), dict)
#
#
# def test_clean_list_of_dic():
#     test_list_of_dict = [
#         {
#             "demo_Tenure": "Tenure_5",
#             "demo_Company": "",
#             "demo_JobLevel": "JobLevel_2",
#             "demo_Location": "Location_1",
#         },
#         {
#             "demo_Tenure": "Tenure_3",
#             "demo_Company": "Company_1",
#             "demo_JobLevel": "JobLevel_5",
#             "demo_Location": "",
#         },
#     ]
#     result_list_of_dict = etl.clean_list_of_dic(test_list_of_dict)
#
#     assert isinstance(result_list_of_dict, list)
#     assert len(test_list_of_dict) == len(result_list_of_dict)
#     assert result_list_of_dict[0].get("demo_Company") is None
#     assert result_list_of_dict[1].get("demo_Location") is None
