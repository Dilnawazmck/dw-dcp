import io
import json

import pandas as pd
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db import raw_sqls
from app.models.dataset_type import DatasetType
from app.models.practice import Practice
from app.models.question import Question
from app.models.response import Response
from app.models.sentiment import Sentiment
from app.models.topic import Topic
from app.services.base_service import BaseService
from app.services.sentiment import _sentiment
from app.services.survey import _survey
from app.utils.app_utils import _hash
from app.utils.dict_utils import safe_get

FILTER_CLAUSE = {
    "topic_id": "r.topic_id IN ({})",
    "practice_id": "r.practice_id IN ({})",
    "question_id": "r.question_id IN ({})",
}


class ResponseService(BaseService):
    __model__ = Response

    @property
    def model_cls(self):
        """Returns a class of model which binds to the service"""
        return self.__model__

    def get_by_id_and_survey_id(self, id: int, survey_id: str, db: Session):
        decoded_survey_id = _hash.decode(survey_id)
        if not decoded_survey_id:
            return None
        return (
            db.query(self.model_cls)
            .filter(
                self.model_cls.id == id, self.model_cls.survey_id == decoded_survey_id
            )
            .first()
        )

    @staticmethod
    def parse_filters(filters):
        if not filters:
            return None
        result = []
        filters = filters.split(";")
        for filter_expr in filters:
            filter_expr_tup = tuple(filter_expr.split(":"))
            result.append(filter_expr_tup)
        return result

    @staticmethod
    def get_response_type(filters, db: Session):
        if not filters:
            return None
        for key, op, val in filters:
            if key == "type":
                response = (
                    db.query(DatasetType.name).filter(DatasetType.id == val).first()
                )
                return response

    @staticmethod
    def convert_swd_data_to_json(data: str):

        if len(data) == 0:
            return []

        d = [(i.split("::")[0], i.split("::")[1]) for i in data.split(",")]

        final_list = []
        for i in d:
            temp_dict = {"name": i[0], "count": i[1]}
            final_list.append(temp_dict)
        return final_list

    @staticmethod
    def add_filters(filters):
        if not filters:
            return "", "", ""
        filter_sql = ""
        exclude_sql = ""
        user_saved_comment_join = ""
        where_clause = " AND "
        practice_filter_flag = False
        for key, op, val in filters:
            if key == "practice_id":
                filter_sql += where_clause + "( r.practice_id IN ({}) )".format(val)
                practice_filter_flag = True
            elif key == "topic_id":
                if practice_filter_flag:
                    filter_sql = filter_sql[:-1]
                    filter_sql += " OR " + " r.topic_id IN ({}) )".format(val)
                else:
                    filter_sql += where_clause + " r.topic_id IN ({}) ".format(val)
            elif key == "sentiment_id":
                filter_sql += where_clause + "r.sentiment_id IN ({}) ".format(val)
            elif key == "question_id":
                filter_sql += where_clause + " r.question_id IN ({})".format(val)
            elif key == "type":
                filter_sql += where_clause + " r.type IN ({})".format(val)
            elif key == "exclude":
                exclude_sql = " WHERE (js).key not in {}".format(
                    str(val.split(",")).replace("[", "(").replace("]", ")")
                )
            elif key == "type_id":
                filter_sql += where_clause + " r.type_id IN ({})".format(val)
            elif key == "search":
                and_or_clause = " AND ("
                for keyword in val.split(","):
                    filter_sql += and_or_clause + " lower(answer) like '%{}%' ".format(
                        keyword.lower()
                    )
                    and_or_clause = " OR "
                filter_sql += " ) "
            elif key == "user_id":
                user_saved_comment_join = (
                    " JOIN user_saved_comment usc on r.id = usc.response_id"
                )
                filter_sql += where_clause + " usc.user_id={}".format(val)
            else:
                filter_sql += where_clause + " filter_json->>'{col}' IN {val}".format(
                    col=key, val=str(val.split(",")).replace("[", "(").replace("]", ")")
                )
        return filter_sql, exclude_sql, user_saved_comment_join

    def get_model_names_by_id(self, table_model: any, model_id: list, db: Session):
        result_list = []
        if not table_model:
            return None
        if not model_id:
            return None

        result = db.query(table_model).filter(table_model.id.in_(model_id)).all()
        for ele in result:
            result_list.append(ele.name)
        return str(",".join(result_list))

    def filter_summary(
        self, filters: list, db: Session, survey_id: str, practice_name: str
    ):
        if not filters:
            return None

        decoded_survey_id = _hash.decode(survey_id)
        if not decoded_survey_id:
            return None

        db_result_summary = []

        for key, op, val in filters:
            if key == "practice_id":
                result = self.get_model_names_by_id(
                    Practice, list(map(int, val.split(","))), db
                )
                db_result_summary.append(practice_name + " practice : " + result)

            if key == "question_id":
                result = self.get_model_names_by_id(
                    Question, list(map(int, val.split(","))), db
                )
                db_result_summary.append("Questions : " + result)

            if key == "topic_id":
                result = self.get_model_names_by_id(
                    Topic, list(map(int, val.split(","))), db
                )
                db_result_summary.append("Workplace themes : " + result)

            if key == "exclude":
                db_result_summary.append("Exclude  :   " + val)

            if key == "search":
                db_result_summary.append("Search  :   " + val)

            if key == "sentiment_id":
                result = self.get_model_names_by_id(
                    Sentiment, list(map(int, val.split(","))), db
                )
                db_result_summary.append("Sentiment : " + result)

            if key[0:4] == "demo":
                sql_response = raw_sqls.GET_FILTER_SUMMARY_DEMOS.format(
                    key=key,
                    demo_values=val.replace(",", "','"),
                    survey_id=decoded_survey_id[0],
                )
                db_result = self.execute_raw_sql(sql_response, db)
                if db_result:
                    demo_name = db_result[0][1] + " : "
                    demo_value = db_result[0][2]
                    list_values_codes = list(val.split(","))

                    for list_values_text in list_values_codes:
                        for ele in demo_value:
                            if list_values_text == ele["column_value"]:
                                demo_name += ele["display_name"] + ","

                    demo_name = str(demo_name)
                    db_result_summary.append(demo_name[:-1])

        return db_result_summary

    @staticmethod
    def transform_demographics(
        survey_id: int, demo_key: str, demo_value: str, db: Session
    ):
        value = None
        survey_data = _survey.get_by_id(survey_id, db)
        display_name = safe_get(safe_get(survey_data.filters, demo_key), "display_name")
        for item in safe_get(
            safe_get(survey_data.filters, demo_key, {}), "options", []
        ):
            if safe_get(item, "column_value") == demo_value:
                value = safe_get(item, "display_name")
                break
        return display_name, value

    @staticmethod
    def transform_response_with_updated_demographics(
        survey_id: int, raw_db_result: list, db: Session
    ):
        response = []
        transformed_filter_json = {}

        for row in raw_db_result:
            row = dict(row)
            for key, value in safe_get(row, "filter_json", {}).items():
                (
                    transformed_key,
                    transformed_value,
                ) = ResponseService.transform_demographics(survey_id, key, value, db)
                transformed_filter_json[transformed_key] = transformed_value
            row["filter_json"] = transformed_filter_json.copy()
            response.append(row)
            transformed_filter_json.clear()
        return response

    @staticmethod
    def invert_filter_dict(input_dict: dict):
        output_dict = {}
        for item in input_dict:
            output_dict = {
                **output_dict,
                **{item["column_value"]: item["display_name"]},
            }
        return output_dict

    @staticmethod
    def create_filter_column_dict(column_list: list, input_dict: dict):
        output_dict = {}
        for item in column_list:
            output_dict = {**output_dict, **{item: input_dict[item]["display_name"]}}
        return output_dict

    @staticmethod
    def comparison_operator(input_value):
        if "lt:" in input_value:
            output_value = input_value.replace("lt:", "<")
        elif "gt:" in input_value:
            output_value = input_value.replace("gt:", ">")
        elif "eq:" in input_value:
            output_value = input_value.replace("eq:", "=")
        return output_value

    def create_export_filter_summary(self, db_filter_summary):

        df_result_filter_summary = pd.DataFrame(
            db_filter_summary, columns=["Filter Summary :"]
        )

        if df_result_filter_summary.empty:
            return df_result_filter_summary

        return df_result_filter_summary

    def create_export_dataframe(
        self,
        response_sql: list,
        filter_dict: dict,
        filter_column_list: list,
        practice_name: str,
    ):

        df_result = pd.DataFrame(
            response_sql,
            columns=[
                "Questions",
                "Comments",
                "Translated answer",
                f"{practice_name} Practice",
                "Workplace themes",
                "Top words",
                "filter_json",
                "Custom themes",
                "Is saved comment",
                "Folder name",
                "Sentiment",
            ],
        )
        if df_result.empty:
            return df_result

        df_result = df_result.join(pd.json_normalize(df_result["filter_json"])).drop(
            "filter_json", axis=1
        )

        new_filter_column_dict = self.create_filter_column_dict(
            filter_column_list, filter_dict
        )

        for k in filter_column_list:
            if k in df_result.columns:
                temp_dict = self.invert_filter_dict(filter_dict[k]["options"])
                df_result[k].replace(temp_dict, inplace=True)

        df_result.rename(columns=new_filter_column_dict, inplace=True)

        return df_result

    def get_popular_words_in_survey(
        self, survey_id: str, group_by: str, filters: str, db: Session
    ):
        decoded_survey_id = _hash.decode(survey_id)
        if not decoded_survey_id:
            return []

        parsed_filters = self.parse_filters(filters)
        filter_sql, exclude_sql, _ = self.add_filters(parsed_filters)
        sql = raw_sqls.GET_TOP_WORDS_IN_SURVEY_SQL.format(
            group_by=group_by,
            survey_id=decoded_survey_id[0],
            top_n=10,
            filter_sql=filter_sql,
            exclude_sql=exclude_sql,
        )
        resp = self.execute_raw_sql(sql, db)
        return resp

    def get_sentiment_count_in_survey(
        self, survey_id: str, group_by: str, filters: str, db: Session, sortby: str
    ):
        decoded_survey_id = _hash.decode(survey_id)
        if not decoded_survey_id:
            return []
        sortby = sortby.replace(":", " ")

        parsed_filters = self.parse_filters(filters)
        filter_sql, exclude_sql, _ = self.add_filters(parsed_filters)
        sql = raw_sqls.GET_SENTIMENTS_COUNTS.format(
            group_by=group_by,
            survey_id=decoded_survey_id[0],
            sentiment_id='{"sentiment_id":',
            sentiment_name=r',"name":"',
            sentiment_count=r'","count":',
            end_string=r"}",
            filter_sql=filter_sql,
            sort_by=sortby,
        )
        resp = self.execute_raw_sql(sql, db)
        return resp

    def get_sentiment_breakdown(self, survey_id: str, filters: str, db: Session):
        decoded_survey_id = _hash.decode(survey_id)
        if not decoded_survey_id:
            return []

        parsed_filters = self.parse_filters(filters)
        filter_sql, _, _ = self.add_filters(parsed_filters)

        total_comments_sql = raw_sqls.GET_TOTAL_COMMENTS_WITH_FILTER.format(
            survey_id=decoded_survey_id[0],
            filter_sql=filter_sql,
            user_saved_comment_join="",
        )
        resp_total_comments = self.execute_raw_sql(total_comments_sql, db)

        sql = raw_sqls.GET_SENTIMENT_BREAKDOWN.format(
            survey_id=decoded_survey_id[0],
            filter_sql=filter_sql,
            sentiment_id='{"sentiment_id":',
            sentiment_name=r',"name":"',
            sentiment_count=r'","count":',
            end_string=r"}",
        )
        resp_sentiment_data = self.execute_raw_sql(sql, db)

        for r in resp_sentiment_data[0][0]:
            if r["name"] == "Positive":
                positive = r["count"]
            if r["name"] == "Negative":
                negative = r["count"]

        sentiment_score = _sentiment.sentiment_score(positive, negative)
        sentiment_list = {"sentiment_data": resp_sentiment_data[0][0]}
        response_final = {
            "total_comments": resp_total_comments[0].count,
            "sentiment_score": sentiment_score,
        }
        response_final.update(sentiment_list)
        return response_final

    def get_sentiment_wise_demographic_scores(
        self,
        survey_id: str,
        filters: str,
        demographic: str,
        sentiment: str,
        nsize: str,
        skip: int,
        limit: int,
        db: Session,
    ):
        decoded_survey_id = _hash.decode(survey_id)
        if not decoded_survey_id:
            return []

        nsize = self.comparison_operator(nsize)

        sentiment = sentiment.replace(":", " ")

        if demographic == "overall":
            demographic = ""
        else:
            demographic = "	where jkey='" + demographic + "'"

        parsed_filters = self.parse_filters(filters)
        filter_sql, _, _ = self.add_filters(parsed_filters)

        sql = raw_sqls.GET_SENTIMENT_WISE_DEMOGRAPHIC_SCORES.format(
            survey_id=decoded_survey_id[0],
            filter_sql=filter_sql,
            demographic=demographic,
            sentiment=sentiment,
            nsize=nsize,
            skip=skip,
            limit=limit,
            type_id='{"practice_name":"',
            count=r'","counts":',
            endoffile="}",
            topic_type_id='{"topic_name":"',
        )
        resp_data = self.execute_raw_sql(sql, db)

        if not resp_data:
            return []

        return {"totaldemos": resp_data[0]["totaldemos"], "listing": resp_data}

    def get_swd_pop_data(self,
                         survey_id: str,
                         filters: str,
                         demographic: str,
                         limit: int,
                         db: Session
                         ):

        decoded_survey_id = _hash.decode(survey_id)
        if not decoded_survey_id:
            return []

        if not demographic:
            return []

        parsed_filters = self.parse_filters(filters)
        filter_sql, _, _ = self.add_filters(parsed_filters)
        demographic = "('" + demographic.replace(',', "','") + "')"
        sql = raw_sqls.GET_SWD_POP_DATA.format(
            survey_id=decoded_survey_id[0],
            filter_sql=filter_sql,
            demographic=demographic,
            limit = limit

        )
        resp_data = self.execute_raw_sql(sql, db)

        final_data = []

        for i in resp_data:
            practice_positive = self.convert_swd_data_to_json(i["practice_positive"])
            topic_positive = self.convert_swd_data_to_json(i["topic_positive"])
            practice_negative = self.convert_swd_data_to_json(i["practice_negative"])
            topic_negative = self.convert_swd_data_to_json(i["topic_negative"])
            practice_neutral = self.convert_swd_data_to_json(i["practice_neutral"])
            topic_neutral = self.convert_swd_data_to_json(i["topic_neutral"])

            temp_dict = {
                "option_code": i["demo_value"],
                "sentiment_neutral": {"practice_data": practice_neutral, "topic_data": topic_neutral},
                "sentiment_positive": {"practice_data": practice_positive, "topic_data": topic_positive},
                "sentiment_negative": {"practice_data": practice_negative, "topic_data": topic_negative}
            }

            final_data.append(temp_dict)
        return final_data


    def get_sentiment_wise_demographic_popup_data(
        self,
        survey_id: str,
        filters: str,
        demographic: str,
        db: Session,
    ):
        decoded_survey_id = _hash.decode(survey_id)
        if not decoded_survey_id:
            return []

        if not demographic:
            return []

        parsed_filters = self.parse_filters(filters)
        filter_sql, _, _ = self.add_filters(parsed_filters)
        demographic = tuple(demographic.split(","))

        sql = raw_sqls.GET_SENTIMENT_WISE_DEMOGRAPHIC_POPUP_DATA.format(
            survey_id=decoded_survey_id[0],
            filter_sql=filter_sql,
            demographic=demographic,
            practice_name='{"practice_name":"',
            count=r'","counts":',
            endoffile="}",
            topic_name='{"topic_name":"',
            option_code='{"option_code": "',
            sentiment_neutral='","sentiment_neutral":{"practice_data":[',
            sentiment_positive=']},"sentiment_positive":{"practice_data":[',
            sentiment_negative=']},"sentiment_negative":{"practice_data":[',
            topic_data='],"topic_data":['
        )
        resp_data = self.execute_raw_sql(sql, db)

        return resp_data



    def get_sentiment_wise_demographic(
        self,
        survey_id: str,
        filters: str,
        demographic: str,
        sentiment: str,
        nsize: str,
        skip: int,
        limit: int,
        db: Session,
    ):
        decoded_survey_id = _hash.decode(survey_id)
        if not decoded_survey_id:
            return []

        nsize = self.comparison_operator(nsize)

        sentiment = sentiment.replace(":", " ")

        if demographic == "overall":
            demographic = ""
        else:
            demographic = "	where jkey='" + demographic + "'"

        parsed_filters = self.parse_filters(filters)
        filter_sql, _, _ = self.add_filters(parsed_filters)
        sql = raw_sqls.GET_SENTIMENT_WISE_DEMOGRAPHICS.format(
            survey_id=decoded_survey_id[0],
            filter_sql=filter_sql,
            demographic=demographic,
            sentiment=sentiment,
            nsize=nsize,
            skip=skip,
            limit=limit,
            type_id='{"practice_name":"',
            count=r'","counts":',
            endoffile="}",
            topic_type_id='{"topic_name":"',
        )
        resp_data = self.execute_raw_sql(sql, db)
        return resp_data

    def get_sentiment_mention_matrix(
        self,
        survey_id: str,
        filters: str,
        group_by: str,
        db: Session,
    ):
        decoded_survey_id = _hash.decode(survey_id)
        if not decoded_survey_id:
            return []
        parsed_filters = self.parse_filters(filters)
        filter_sql, _, _ = self.add_filters(parsed_filters)
        sql = raw_sqls.GET_SENTIMENT_MENTION_MATRIX.format(
            group_by=group_by,
            survey_id=decoded_survey_id[0],
            filter_sql=filter_sql,
            table_name=group_by.replace("_id", ""),
        )
        data = self.execute_raw_sql(sql, db)

        return data


    def get_sentiment_mention_matrix_popup(
        self,
        survey_id: str,
        filters: str,
        group_by: str,
        group_by_id:int,
        db: Session,
    ):
        decoded_survey_id = _hash.decode(survey_id)
        if not decoded_survey_id:
            return []
        parsed_filters = self.parse_filters(filters)
        filter_sql, _, _ = self.add_filters(parsed_filters)
        sql = raw_sqls.GET_SENTIMENT_MENTION_MATRIX_POPUP.format(
            group_by=group_by,
            survey_id=decoded_survey_id[0],
            filter_sql=filter_sql,
            group_by_id=group_by_id
        )
        data = self.execute_raw_sql(sql, db)

        return data

    def get_demographic_heatmap(
        self,
        survey_id: str,
        filters: str,
        group_by: str,
        demographic: str,
        skip: int,
        limit: int,
        db: Session,
    ):
        decoded_survey_id = _hash.decode(survey_id)
        if not decoded_survey_id:
            return []
        parsed_filters = self.parse_filters(filters)
        filter_sql, _, _ = self.add_filters(parsed_filters)
        sql = raw_sqls.GET_DEMOGRAPHIC_HEATMAP.format(
            group_by=group_by,
            survey_id=decoded_survey_id[0],
            filter_sql=filter_sql,
            demographic=demographic,
            skip=skip,
            limit=limit,
            table_name=group_by.replace("_id", ""),

        )
        data = self.execute_raw_sql(sql, db)
        return data

    def get_comments_in_survey_group_by(
        self,
        survey_id: str,
        group_by: str,
        filters: str,
        mention_type: str,
        order_by: str,
        db: Session,
    ):
        decoded_survey_id = _hash.decode(survey_id)
        if not decoded_survey_id:
            return []

        parsed_filters = self.parse_filters(filters)
        filter_sql, _, _ = self.add_filters(parsed_filters)
        sql = raw_sqls.GET_COMMENTS_COUNT_PER_GROUP_SQL.format(
            group_by=group_by,
            survey_id=decoded_survey_id[0],
            filter_sql=filter_sql,
            mention_type=mention_type,
            order_by=order_by,
        )
        return self.execute_raw_sql(sql, db)

    def get_survey_responses(
        self,
        survey_id: str,
        db: Session,
        filters: str,
        folder_name: str,
        user_id: int,
        order_by: str,
        user_saved_comment_join_type: str,
        skip: int = 0,
        limit: int = 10,
    ):
        decoded_survey_id = _hash.decode(survey_id)

        if not decoded_survey_id:
            return {"total_comments": 0, "data": []}

        if order_by == "topic":
            order_by_column = "topic_similarity_score"
        else:
            order_by_column = "practice_similarity_score"

        if len(folder_name) > 0:
            folder_name = " and folder_name = '" + folder_name + "'"
        else:
            folder_name = ""

        parsed_filters = self.parse_filters(filters)
        filter_sql, _, user_saved_comment_join = self.add_filters(parsed_filters)
        total_comments_sql = raw_sqls.GET_TOTAL_COMMENTS_WITH_FILTER.format(
            survey_id=decoded_survey_id[0],
            filter_sql=filter_sql,
            user_saved_comment_join=user_saved_comment_join,
        )
        sql = raw_sqls.GET_SURVEY_RESPONSES.format(
            survey_id=decoded_survey_id[0],
            filter_sql=filter_sql,
            user_id=user_id,
            user_saved_comment_join_type=user_saved_comment_join_type,
            limit=limit,
            offset=skip,
            order_by=order_by_column,
            folder_name=folder_name,
        )
        total_comments = self.execute_raw_sql(total_comments_sql, db)
        db_result = self.execute_raw_sql(sql, db)

        # Update demographics dict with actual key value
        response = self.transform_response_with_updated_demographics(
            decoded_survey_id[0], db_result, db
        )

        return {"total_comments": total_comments[0].count, "data": response}

    def get_survey_wordcloud(
        self, survey_id: str, db: Session, filters: str, limit: int = 10
    ):
        decoded_survey_id = _hash.decode(survey_id)
        if not decoded_survey_id:
            return []

        parsed_filters = self.parse_filters(filters)
        filter_sql, exclude_sql, _ = self.add_filters(parsed_filters)
        sql = raw_sqls.GET_WORDCLOUD_WITH_FILTER_SQL.format(
            survey_id=decoded_survey_id[0],
            filter_sql=filter_sql,
            exclude_sql=exclude_sql,
            limit=limit,
        )
        db_result = self.execute_raw_sql(sql, db)
        return db_result

    def get_survey_excel(
        self,
        survey_id: str,
        db: Session,
        filters: str,
        user_id: int,
        is_saved_comments: bool,
        excel_name: str,
    ):
        decoded_survey_id = _hash.decode(survey_id)
        if not decoded_survey_id:
            return []

        parsed_filters = self.parse_filters(filters)
        filter_sql, _, _ = self.add_filters(parsed_filters)

        practice_name = self.get_response_type(parsed_filters, db=db)
        if not practice_name:
            practice_name = ("OHI",)
        result_summary = self.filter_summary(
            parsed_filters, db, survey_id=survey_id, practice_name=practice_name[0]
        )

        if is_saved_comments:
            sql_response = raw_sqls.GET_SAVED_RESPONSE_EXPORT_SQL.format(
                survey_id=decoded_survey_id[0], filter_sql=filter_sql, user_id=user_id
            )
        else:
            sql_response = raw_sqls.GET_RESPONSE_EXPORT_SQL.format(
                survey_id=decoded_survey_id[0], filter_sql=filter_sql, user_id=user_id
            )

        db_result = self.execute_raw_sql(sql_response, db)

        sql_survey_filter = raw_sqls.GET_SURVEY_FILTER_SQL.format(
            survey_id=decoded_survey_id[0]
        )
        survey_filter = self.execute_raw_sql(sql_survey_filter, db)

        survey_filter_dict = survey_filter[0][0]
        survey_filter_columns = survey_filter[0][1]

        final_response_df_main = self.create_export_dataframe(
            db_result, survey_filter_dict, survey_filter_columns, practice_name[0]
        )

        stream = io.BytesIO()
        writer = pd.ExcelWriter(stream, engine="xlsxwriter")
        if result_summary:
            final_response_df_filter_summary = self.create_export_filter_summary(
                result_summary
            )
            final_response_df_filter_summary.to_excel(
                writer, sheet_name="Filter_Summary", index=False, startcol=1
            )
        final_response_df_main.to_excel(writer, sheet_name="Data", index=False)
        writer.save()
        response = StreamingResponse(iter([stream.getvalue()]))
        response.headers["Content-Disposition"] = (
            "attachment; filename=" + excel_name + ".xlsx"
        )

        return response


_response = ResponseService()
