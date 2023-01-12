import csv
import json
import os
import re
import shutil
from collections import defaultdict
from datetime import datetime
from io import StringIO

import numpy as np
import pandas as pd
import spacy
import tensorflow_hub as hub
import tensorflow_text as text
from easynmt import EasyNMT
from nltk.corpus import stopwords

from app.core import config
from app.core.config import logger
from app.db.session import get_db_session
from app.models.practice import Practice
from app.services.sentiment import _sentiment
from app.services.sentiment_analysis import get_sentiment, load_custom_model
from app.services.text_classification import get_similar_theme
from app.services.topic import _topic
from app.services.wordcloud import get_words_with_frequency_from_document
from app.utils import dict_utils, str_utils
from app.utils.constants import COMMENT_LENGTH_FOR_TAGGING

USE_MODEL = hub.load(
    "https://tfhub.dev/google/universal-sentence-encoder-multilingual-large/3"
)

SPACY_MODEL = spacy.load("en_core_web_lg")

TRANSLATION_MODEL = EasyNMT("m2m_100_1.2B")

SENTIMENT_MODEL = load_custom_model(
    model_path=config.SENTIMENT_MODEL_PATH, model_bucket=config.AWS_BUCKET
)

CHUNK_SIZE = config.DATA_CHUNK_SIZE

COLUMN_LIST_RESPONSE = [
    "last_updated_on",
    "created_on",
    "is_deleted",
    "question_id",
    "answer",
    "filter_json",
    "survey_id",
    "answer_lang",
    "translated_en_answer",
    "sentiment_id",
    "is_sentiment_verified",
    "topic_id",
    "is_topic_verified",
    "practice_id",
    "is_practice_verified",
    "top_words",
    "confirmit_resp_id",
    "topic_similarity_score",
    "practice_similarity_score",
    "sentiment_score",
    "type",
]
COLUMN_LIST_QUESTION = [
    "last_updated_on",
    "created_on",
    "is_deleted",
    "name",
    "survey_id",
    "type",
]

EN_STOPWORDS: list = stopwords.words("english")


def get_stopwords_dict():
    stopwords_dict = defaultdict(int)
    for stopword in EN_STOPWORDS:
        stopwords_dict[stopword] += 1
    return stopwords_dict


def insert_client_table(connection, data_file_path):
    metadata = read_json_file(data_file_path[1])

    client_name = dict_utils.safe_get(metadata, "client_name")
    if not client_name:
        raise Exception("Client name not present in metadata.")

    select_query = "SELECT * from client where name=%s"
    insert_query = "INSERT into client(last_updated_on,created_on,is_deleted,name)\
        values (current_timestamp,current_timestamp,false,%s) \
        RETURNING id"
    result = execute_single_query(connection, select_query, client_name)
    if not result:
        # insert client and return id
        result = execute_single_query(connection, insert_query, client_name)

    return result


def insert_survey_table(connection, project_id, client_id, data_file_path):
    metadata = read_json_file(data_file_path[1])

    survey_name = dict_utils.safe_get(metadata, "survey_name")
    if not survey_name:
        raise Exception("Survey name not present in metadata.")

    survey_type = dict_utils.safe_get(metadata, "survey_type")
    if not survey_name:
        raise Exception("Survey type not present in metadata.")

    filter_data = dict_utils.safe_get(metadata, "filters")
    if not filter_data:
        raise Exception("filters key not present in metadata.")

    filter_dict = list_to_dict(filter_data)

    select_query = "SELECT * from survey where client_id=%s and confirmit_pid=%s"
    insert_query = "INSERT into survey(last_updated_on,created_on,is_deleted,name,confirmit_pid,client_id,filters,type)\
        values (current_timestamp,current_timestamp,false,%s,%s,%s,%s,%s) RETURNING id"
    update_query = (
        "UPDATE survey set last_updated_on=current_timestamp,is_deleted=false,name=%s,confirmit_pid=%s,"
        "filters=%s,type=%s where client_id=%s and confirmit_pid=%s RETURNING id"
    )

    result = execute_single_query(connection, select_query, client_id, project_id)
    if result:
        # update client and return id
        result = execute_single_query(
            connection,
            update_query,
            survey_name,
            project_id,
            filter_dict,
            survey_type,
            client_id,
            project_id,
        )
    else:
        # insert
        result = execute_single_query(
            connection,
            insert_query,
            survey_name,
            project_id,
            client_id,
            filter_dict,
            survey_type,
        )

    return result


def insert_question_table(connection, survey_id, data_file_path):
    metadata = read_json_file(data_file_path[1])

    data_question = dict_utils.safe_get(metadata, "data")
    if not data_question:
        raise Exception("Data question key not present in metadata.")

    temp_data_list = []
    for item in data_question:
        if not item["display_name"]:
            raise Exception(
                "Required key - 'display_name' not present in data question list"
            )
        temp_data_list.append(
            [
                datetime.now(),
                datetime.now(),
                "false",
                re.sub("[\n|\r]", " ", item["display_name"]),
                survey_id,
                item["type"],
            ]
        )

    df_question = pd.DataFrame(temp_data_list, columns=COLUMN_LIST_QUESTION)

    select_query = "SELECT * from question where survey_id=%s"
    result = execute_single_query(connection, select_query, survey_id)
    if not result:
        # insert data
        copy_df_to_table(
            connection, df_question, "question", "|", tuple(COLUMN_LIST_QUESTION)
        )


def insert_response_table(
    connection, db_session, survey_id, data_file_path, project_id
):
    df_data_csv = read_csv_file(data_file_path[0])

    metadata = read_json_file(data_file_path[1])

    data_question = dict_utils.safe_get(metadata, "data")
    data_filter = dict_utils.safe_get(metadata, "filters")
    if not data_question or not data_filter:
        raise Exception(
            f"{project_id} - Cannot fetch questions/data dictionaries from metadata."
        )

    list_input_data_column = [
        [item["column_name"], item["type"]] for item in data_question
    ]  # list of data columns in csv
    list_input_data_filter = [
        item["column_name"] for item in data_filter
    ]  # list of filter columns in csv

    if len(list_input_data_column) == 0 or len(list_input_data_filter) == 0:
        raise Exception(
            f"{project_id} - list_input_data_column/list_input_data_filter is blank."
        )

    # replacing nan with blank value for filter columns
    for item in list_input_data_filter:
        df_data_csv[item].replace(np.nan, "", inplace=True)

    # converting dataframe to dict and remove blank keys in the list
    demogdict_temp = df_data_csv[list_input_data_filter].to_dict("records")
    demog_dict_list = clean_list_of_dic(demogdict_temp)

    df_data_csv["filter_json"] = [json.dumps(item) for item in demog_dict_list]
    df_data_csv.drop(list_input_data_filter, axis=1, inplace=True)

    question_types = [item[1] for item in list_input_data_column]
    question_types = np.unique(np.array(question_types))
    question_types = [np.int16(item).item() for item in question_types]

    for q_type in question_types:
        select_query = "SELECT * from question where survey_id=%s and type=%s"
        result = execute_query(connection, select_query, survey_id, q_type)
        if not result:
            raise Exception(
                f"{project_id} - Cannot fetch question result from question table for survey id - {survey_id}"
            )

        question_id_list = [row[0] for row in result]

        transpose_df = transpose_data(
            df_data_csv,
            [item[0] for item in list_input_data_column if item[1] == q_type],
            ["answer", "filter_json", "question_id", "confirmit_resp_id", "type"],
            question_id_list,
            q_type,
        )

        transpose_df = get_df_based_on_last_inserted_id(
            transpose_df, connection, survey_id, project_id, q_type
        )

        logger.info(f"{project_id} - Chunk size is {CHUNK_SIZE}")
        logger.info(
            f"{project_id} - Total comments to push into DB - {len(transpose_df.index)}"
        )

        while not transpose_df.empty:
            final_df_response = create_final_response_dataframe(
                db_session,
                transpose_df[:CHUNK_SIZE],
                survey_id,
                COLUMN_LIST_RESPONSE,
                project_id,
                q_type,
            )
            transpose_df = transpose_df[CHUNK_SIZE:]

            if not final_df_response.empty:
                copy_df_to_table(
                    connection,
                    final_df_response,
                    "response",
                    "\t",
                    tuple(COLUMN_LIST_RESPONSE),
                )
                connection.commit()


def get_df_based_on_last_inserted_id(
    transpose_df: pd.DataFrame, connection, survey_id, project_id, q_type
):
    select_query = (
        "SELECT MAX(confirmit_resp_id) from response where survey_id=%s and type=%s"
    )
    result = execute_query(connection, select_query, survey_id, q_type)
    last_confirmit_resp_id = result[0][0]

    # Checking if above last_confirmit_resp_id exists in dataframe
    if last_confirmit_resp_id:
        if transpose_df[
            transpose_df["confirmit_resp_id"] == last_confirmit_resp_id
        ].empty:
            raise Exception(
                f"{project_id} - last response id not found in transposed dataframe"
            )
        else:
            delete_query = "delete from response where survey_id=%s and confirmit_resp_id=%s  RETURNING id"
            result = execute_query(
                connection, delete_query, survey_id, last_confirmit_resp_id
            )
            if not result:
                raise Exception(
                    f"{project_id} - Deletion of last response id inserted failed."
                )
            transpose_df = transpose_df[
                transpose_df["confirmit_resp_id"] >= last_confirmit_resp_id
            ]

    if transpose_df.empty:
        raise Exception(
            f"{project_id} - Nothing to push, filtered data frame is empty."
        )

    return transpose_df


def get_topics_metadata(db_session):
    topics = _topic.get_all(db_session)
    topic_dict = {topic.name: topic.id for topic in topics}

    inner_list = []
    topics_with_context = []
    for topic in topics:
        inner_list.append(topic.name)
        inner_list.extend(topic.context)
        topics_with_context.append(inner_list.copy())
        inner_list.clear()

    return topics_with_context, topic_dict


def get_practice_metadata(db_session, type):
    practices = db_session.query(Practice).filter(Practice.type == type).all()
    practice_dict = {practice.name: practice.id for practice in practices}

    inner_list = []
    practices_with_context = []
    for practice in practices:
        inner_list.append(practice.name)
        inner_list.extend(practice.context)
        practices_with_context.append(inner_list.copy())
        inner_list.clear()
    return practices_with_context, practice_dict


def get_sentiment_metadata(db_session):
    sentiments = _sentiment.get_all(db_session)
    sentiment_dict = {sentiment.name: sentiment.id for sentiment in sentiments}
    return sentiment_dict


def create_final_response_dataframe(
    db_session, tmp_df_output, survey_id, final_df_column_list, project_id, type
):
    answer_lang = []
    translated_en_answer = []
    words_list = []
    final_df = pd.DataFrame(columns=final_df_column_list)

    final_df["question_id"] = tmp_df_output["question_id"]
    final_df["answer"] = tmp_df_output["answer"]
    final_df["filter_json"] = tmp_df_output["filter_json"]
    final_df["confirmit_resp_id"] = tmp_df_output["confirmit_resp_id"].astype(int)
    final_df["last_updated_on"] = datetime.now()
    final_df["created_on"] = datetime.now()
    final_df["is_deleted"] = "false"
    final_df["survey_id"] = survey_id
    final_df["type"] = tmp_df_output["type"]

    logger.info(f"{project_id} - response raw data ends, NLP Start")

    # Adding NLP columns
    en_stopwords_dict: dict = get_stopwords_dict()
    translated = ""
    for index, row in tmp_df_output.iterrows():
        lang = detect_lang(row["answer"])
        if lang != "en":
            try:
                translated = TRANSLATION_MODEL.translate(
                    row["answer"], target_lang="en", source_lang=lang
                )
            except Exception as e:
                logger.info(
                    "{} - Unable to translate for lang {} : {}".format(
                        project_id, lang, row["answer"]
                    )
                )
                logger.info("{} - Error raised is : {}".format(project_id, str(e)))
                translated = row["answer"]
        words_list.append(
            json.dumps(
                get_words_with_frequency_from_document(
                    doc=row["answer"] if lang == "en" else translated,
                    stopwords_dict=en_stopwords_dict,
                    nlp=SPACY_MODEL,
                )
            )
        )
        answer_lang.append(lang)
        translated_en_answer.append(None if lang == "en" else translated)

    final_df["answer_lang"] = answer_lang
    final_df["translated_en_answer"] = translated_en_answer
    final_df["top_words"] = words_list

    practices_with_context, practice_dict = get_practice_metadata(
        db_session, 1 if type == 4 else type
    )
    topics_with_context, topic_dict = get_topics_metadata(db_session)
    sentiment_dict = get_sentiment_metadata(db_session)

    topic_list, topic_score_list = get_similar_theme(
        tmp_df_output["answer"].str.slice(0, COMMENT_LENGTH_FOR_TAGGING),
        topics_with_context,
        USE_MODEL,
    )
    practices_list, practice_score_list = get_similar_theme(
        tmp_df_output["answer"].str.slice(0, COMMENT_LENGTH_FOR_TAGGING),
        practices_with_context,
        USE_MODEL,
    )

    final_df["topic_id"] = [topic_dict[theme] for theme in topic_list]
    final_df["practice_id"] = [practice_dict[practice] for practice in practices_list]

    final_df["topic_similarity_score"] = topic_score_list
    final_df["practice_similarity_score"] = practice_score_list

    sentiment_list, sentiment_score_list = get_sentiment(
        final_df["answer"], SENTIMENT_MODEL
    )

    final_df["sentiment_id"] = [
        sentiment_dict[sentiment] for sentiment in sentiment_list
    ]
    final_df["sentiment_score"] = sentiment_score_list

    logger.info(f"{project_id} - NLP End")

    return final_df


def text_cleaning_dataframe(tmp_df_output):

    tmp_df_output.replace(r"\n|\r|\t|\\|-", "", regex=True, inplace=True)
    tmp_df_output["answer"].replace(
        r"^[!#$%&\'()*+,-./:;<=>?@[\]^_`{|}~]*$", np.nan, regex=True, inplace=True
    )
    tmp_df_output["answer"].replace(
        r"^[nNaANnOonNeEnN/aA]*$", np.nan, regex=True, inplace=True
    )
    tmp_df_output.loc[
        tmp_df_output["answer"].map(str).apply(len) < 3, "answer"
    ] = np.nan
    tmp_df_output["answer"].replace("", np.nan, inplace=True)
    tmp_df_output.dropna(axis=0, inplace=True, subset=["answer"])
    return tmp_df_output


def detect_lang(text_to_detect_lang):
    lang = TRANSLATION_MODEL.language_detection_fasttext(text_to_detect_lang)
    if lang in ["yue", "wuu", "min"]:
        lang = "zh"
    return lang


def transpose_data(
    input_df_csv, data_column_list, output_column_list, question_id_list, q_type
):
    tmp_df_output = pd.DataFrame(columns=output_column_list)
    i = 0
    for item in data_column_list:
        dfquestionid = pd.DataFrame(
            {"question_id": [question_id_list[i]] * len(input_df_csv)}
        )
        dfquestiontype = pd.DataFrame({"type": [q_type] * len(input_df_csv)})
        tempdf = pd.concat(
            [
                input_df_csv[item],
                input_df_csv["filter_json"],
                dfquestionid,
                input_df_csv["responseid"],
                dfquestiontype,
            ],
            axis=1,
            ignore_index=True,
        )
        tempdf.columns = tmp_df_output.columns
        tmp_df_output = pd.concat([tmp_df_output, tempdf], ignore_index=True)
        i += 1

    # Sorting, cleaning and removing blank answers
    tmp_df_output.sort_values("confirmit_resp_id", inplace=True)
    final_tmp_df_output = text_cleaning_dataframe(tmp_df_output)

    return final_tmp_df_output


def read_json_file(file_path):
    if not os.path.exists(file_path):
        raise Exception("Metadata file does not exist in the given path.")
    with open(file_path, encoding="utf8") as f:
        data = json.load(f)
    return data


def read_csv_file(file_path):
    if not os.path.exists(file_path):
        raise Exception("CSV data file does not exist in the given path.")
    with open(file_path, encoding="utf8") as f:
        data = pd.read_csv(f, skipinitialspace=True)

    if data.empty:
        raise Exception("CSV Data file is empty.")
    return data


def list_to_dict(data_list):
    dict_new = {}
    if not data_list or len(data_list) == 0:
        raise Exception("Input filter list is empty.")

    for item in data_list:
        if not item["column_name"] or not item["display_name"] or not item["options"]:
            raise Exception("Required keys are not present in the input list")
        dict_new[item["column_name"]] = {}
        dict_new[item["column_name"]]["display_name"] = item["display_name"]
        dict_new[item["column_name"]]["options"] = item["options"]

    return json.dumps(dict_new)


def clean_list_of_dic(input_list_of_dict):
    if not input_list_of_dict:
        return None
    output_list_of_dict = []
    for d in input_list_of_dict:
        clean_dict = {k: v for k, v in d.items() if str_utils.safe_strip(v)}
        output_list_of_dict.append(clean_dict)
    return output_list_of_dict


def execute_query(connection, query, *param):
    cursor = connection.cursor()
    cursor.execute(query, param)
    result = cursor.fetchall()
    cursor.close()
    if not result:
        return None
    return result


def execute_single_query(connection, query, *param):
    cursor = connection.cursor()
    cursor.execute(query, param)
    row = cursor.fetchone()
    cursor.close()
    if not row:
        return None
    return row[0]


def copy_df_to_table(connection, input_df, table_name, csv_sep, table_columns_tuple):
    buffer = StringIO()
    input_df.to_csv(
        buffer, header=False, sep=csv_sep, index=False, quoting=csv.QUOTE_NONE
    )
    buffer.seek(0)
    cursor = connection.cursor()
    cursor.copy_from(
        buffer, table_name, sep=csv_sep, null="", columns=table_columns_tuple
    )
    cursor.close()


def remove_files(folder):
    if os.path.exists(folder):
        shutil.rmtree(folder)


def etl(project_id, data_file_path, temp_base_folder):
    # project_id --> is the name/confirmit pid of the project.
    # data_file_path --> is a list containing absolute file paths of data.csv and metadata.json respectively.
    # temp_base_folder --> absolute path of the folder where data.csv and metadata.json are located.

    logger.info(data_file_path)
    logger.info(f"initiating data push for project - {project_id}")
    db_session = next(get_db_session())

    conn = db_session.connection().connection
    client_id = insert_client_table(conn, data_file_path)
    if not client_id:
        logger.error(f"{project_id} - Client id not generated.")
        raise Exception(f"{project_id} - Client id not generated.")

    survey_id = insert_survey_table(conn, project_id, client_id, data_file_path)
    if not survey_id:
        logger.error(f"{project_id} - Survey id not generated.")
        raise Exception(f"{project_id} - Survey id not generated.")

    logger.info(
        f"{project_id} - Client id is - {client_id}, survey id is - {survey_id}"
    )

    insert_question_table(conn, survey_id, data_file_path)
    insert_response_table(conn, db_session, survey_id, data_file_path, project_id)

    logger.info(f"{project_id} - Data push completed!")
    return client_id, survey_id


if __name__ == "__main__":
    pass
    # etl("p192873", ["tmp/nop4/data.csv", "tmp/nop4/metadata.json"], '')
