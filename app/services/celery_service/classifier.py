import csv
import math
import pandas as pd
import tensorflow_hub as hub
import tensorflow_text as text
import traceback
from celery import Celery
from datetime import datetime
from sqlalchemy.orm import Session
from io import StringIO

from app.core.config import logger, REDIS_URI, DATA_CHUNK_SIZE, APP_DOMAIN_URL
from app.db.session import get_db_session
from app.db import raw_sqls
from app.models.custom_topics_job import CustomTopicsJob
from app.services.custom_topics_job import _custom_topics_job
from app.services.user_topics import _user_topics
from app.services.user_topics_response import _user_topics_response
from app.services.response import _response
from app.services.text_classification import get_similar_theme

from app.utils.constants import CustomTopicsJobStatus
from app.utils.email_utils import send_email

USE_MODEL = hub.load(
    "https://tfhub.dev/google/universal-sentence-encoder-multilingual-large/3"
)

COLUMN_LIST_USER_TOPICS_RESPONSE = [
    "last_updated_on",
    "created_on",
    "is_deleted",
    "response_id",
    "user_id",
    "user_topic_id",
    "topic",
    "topic_similarity_score"
]

CHUNK_SIZE = DATA_CHUNK_SIZE

app = Celery(__name__)
app.conf.broker_url = REDIS_URI


@app.task
def custom_topic_classification(job_id: int, is_edit: bool = False):
    offset = 0
    logger.info("Celery Classifier: job started")
    db = next(get_db_session())

    # get topics list from job_id
    job_obj = _custom_topics_job.get_by_id(id=job_id, db=db)
    topics_obj = _user_topics.get_by_id(id=job_obj.user_topic_id, db=db)
    logger.info(f"Celery Classifier: job id is:- {job_obj.id}")
    try:
        if job_obj.status in [CustomTopicsJobStatus.PROCESSING.value, CustomTopicsJobStatus.COMPLETE.value,
                              CustomTopicsJobStatus.FAIL.value]:
            return None
        logger.info(f"Celery Classifier: is Edit:- {is_edit}")
        if is_edit:
            query = raw_sqls.DELETE_USER_TOPICS_RESPONSE_BY_USERID_AND_SURVEYID.format(
                user_id=topics_obj.user_id,
                survey_id=topics_obj.survey_id
            )
            _user_topics_response.execute_dml_raw_sql(query=query, db=db)

        topics_list = [[item['name']] for item in topics_obj.topics]
        logger.info(f"Celery Classifier: topic list generated:- {topics_list}")
        # check if survey response exists in user_topics_response, if yes then get the max response id
        query = raw_sqls.GET_MAX_RESPONSE_ID_BY_USER_TOPIC.format(
            survey_id=job_obj.survey_id,
            user_id=topics_obj.user_id
        )
        last_id = _response.execute_raw_sql(query=query, db=db)

        # check total number of chunks to be processed for the survey
        logger.info(f"Celery Classifier: last id is:- {last_id[0][0]}")
        if last_id[0][0]:
            where_clause = "where survey_id={survey_id} and id>{last_id}".format(
                survey_id=job_obj.survey_id,
                last_id=last_id[0][0]
            )
        else:
            where_clause = "where survey_id={survey_id}".format(
                survey_id=job_obj.survey_id
            )

        query = "select count(*) from response {where_clause}".format(where_clause=where_clause)
        total_comments_to_process = _response.execute_raw_sql(query=query, db=db)

        total_iteration = math.ceil(total_comments_to_process[0][0]/CHUNK_SIZE)

        limit = CHUNK_SIZE
        if total_comments_to_process[0][0] < CHUNK_SIZE:
            limit = total_comments_to_process[0][0]

        logger.info(f"Celery Classifier: limit is:- {limit}")
        logger.info(f"Celery Classifier: total iteration is:- {total_iteration}")
        logger.info(f"Celery Classifier: chunk size is:- {CHUNK_SIZE}")
        update_job_status(job_obj, CustomTopicsJobStatus.PROCESSING.value, db=db)
        logger.info(f"Celery Classifier: job status changed to processing.")
        conn = db.connection().connection

        for x in range(total_iteration):
            logger.info(f"Celery Classifier: iteration number:- {x}")
            query = raw_sqls.GET_SURVEY_ANSWERS.format(
                where_clause=where_clause,
                limit=limit,
                offset=offset
            )
            response_result = _response.execute_raw_sql(query=query, db=db)
            df_response = pd.DataFrame(response_result, columns=['id', 'answer'])
            logger.info(f"Celery Classifier: input response df created")
            df_user_topics_response = create_dataframe_user_response(
                input_df=df_response,
                column_list=COLUMN_LIST_USER_TOPICS_RESPONSE,
                user_id=topics_obj.user_id,
                user_topic_id=topics_obj.id,
                topics_list=topics_list
            )
            logger.info(f"Celery Classifier: user topics response df created")

            copy_df_to_table(
                connection=conn,
                input_df=df_user_topics_response,
                table_name="user_topics_response",
                csv_sep="\t",
                table_columns_tuple=tuple(COLUMN_LIST_USER_TOPICS_RESPONSE)
            )
            logger.info(f"Celery Classifier: data push complete for iteration {x}")
            conn.commit()
            offset = offset + CHUNK_SIZE

        # if process is completed update status of job as completed
        update_job_status(job_obj, CustomTopicsJobStatus.COMPLETE.value, db=db)
        logger.info(f"Celery Classifier: job status changed to complete.")
        # send success mail
        send_email(
            subject="Text Analytics: Your new list is ready for you to view",
            body_text="We've finished building your new custom list! Please login to Text Analytics to view it:"
                      f" {APP_DOMAIN_URL}\n\nThank you!",
            receiver_emails=[topics_obj.user.email]
        )
        logger.info(f"Celery Classifier: success mail sent to:- {topics_obj.user.email}")
    except Exception:
        logger.info(f"Celery Classifier: exception occurred.")
        update_job_status(job_obj, CustomTopicsJobStatus.FAIL.value, db=db)
        fp = StringIO()
        traceback.print_exc(file=fp)
        stack_trace_msg = fp.getvalue()
        logger.error(stack_trace_msg)
        # send exception email to helpdesk and send job failed email to user
        send_email(
            subject="Text Analytics: Your custom list job failed",
            body_text="Your custom list classification job has failed for report: {survey_name}. Please log "
                      "into your dashboard to re-run the job. If the issue persists, please reach out to "
                      "OHI-Helpdesk ohi-helpdesk@mckinsey.com\n\nTeam Text Analytics".format(
                        survey_name=topics_obj.survey.name),
            receiver_emails=[topics_obj.user.email]
        )

        send_email(
            subject="Custom topics classification job failed",
            body_text="Custom topics classification job has failed for survey {survey_name}.\n\n{stack_trace}".format(
                survey_name=topics_obj.survey.name,
                stack_trace=stack_trace_msg
            )
        )
        logger.info(f"Celery Classifier: failure email sent. {topics_obj.user.email}")

    return job_id


def create_dataframe_user_response(
        input_df: pd.DataFrame, column_list: list, user_id: int, user_topic_id: int, topics_list: list
):
    df_user_topics_response = pd.DataFrame(columns=column_list)
    df_user_topics_response["response_id"] = input_df["id"]
    df_user_topics_response["last_updated_on"] = datetime.now()
    df_user_topics_response["created_on"] = datetime.now()
    df_user_topics_response["is_deleted"] = "false"
    df_user_topics_response["user_id"] = user_id
    df_user_topics_response["user_topic_id"] = user_topic_id
    logger.info(f"Celery Classifier: before similarity")
    topics_list, topics_score_list = get_similar_theme(
        input_df["answer"], topics_list, USE_MODEL
    )
    logger.info(f"Celery Classifier: after similarity.")
    df_user_topics_response["topic"] = topics_list
    df_user_topics_response["topic_similarity_score"] = topics_score_list

    return df_user_topics_response


def update_job_status(
        job_obj: CustomTopicsJob, status: str, db: Session
):
    update_dict = {"status": status}
    _custom_topics_job.update(db_obj=job_obj, update_data=update_dict, db=db)


def copy_df_to_table(
        connection, input_df, table_name, csv_sep, table_columns_tuple
):
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


# custom_topic_classification(29)
