import json
import os
import tempfile
import traceback
from io import StringIO
from pathlib import Path

from app.core import config
from app.core.config import logger
from app.services.data_ingestion.etl import etl
from app.utils.aws_utils import (
    download_files,
    files_exist_in_bucket,
    get_all_keys,
    get_nested_file_paths,
    get_sqs_queue,
)
from app.utils.email_utils import send_email


def process_message(message_body):
    for record in message_body["Records"]:
        s3_keys = get_all_keys(record)

        if not s3_keys["bucket"] or not s3_keys["folder"]:
            raise Exception(
                "Invalid message received. Bucket/folder key not present in the message."
            )

        s3_file_path = get_nested_file_paths(
            s3_keys["folder"], [config.S3_DATAFILE, config.S3_METADATAFILE]
        )

        temp_base_folder = tempfile.TemporaryDirectory(s3_keys["folder"])

        data_file_path = [
            os.path.join(Path(temp_base_folder.name), Path(config.S3_DATAFILE)),
            os.path.join(Path(temp_base_folder.name), Path(config.S3_METADATAFILE)),
        ]

        files_exist_in_bucket(s3_keys["bucket"], s3_file_path)

        download_files(s3_keys["bucket"], s3_file_path, data_file_path)
        # PROCESS etl
        result = etl(s3_keys["folder"], data_file_path, temp_base_folder.name)
        return result[0], result[1], s3_keys["folder"]


def send_email_etl(p_id, c_id, s_id):
    subject = (
        f"Text Analytics:- Project {p_id} has been pushed into the DB successfully!"
    )
    body_text = (
        f"Hi,\n\nProject {p_id} has been pushed into the DB successfully! Below are client and survey "
        f"details.\n\nClient id:- {c_id}\nSurvey id:- {s_id}"
    )
    send_email(subject, body_text)


def send_exception_email(queue_msg, stack_trace):
    subject = "Text Analytics[ERROR]"
    body_text = (
        f"Hi,\n\nError occurred for below project."
        f"\n\nQueue Message:-\n{queue_msg}"
        f"\n\nstack trace:-\n{stack_trace}"
    )
    send_email(subject, body_text)


if __name__ == "__main__":
    while True:
        messages = get_sqs_queue(config.SQS_QUEUE).receive_messages()

        for message in messages:
            logger.info("message received")
            logger.info(message.body)
            try:
                json_obj = json.loads(message.body)
                message.delete()
                logger.info("Message deleted from queue and processing starts.")
                client_id, survey_id, project_id = process_message(json_obj)
                send_email_etl(project_id, client_id, survey_id)
                logger.info("Success email sent.")
            except Exception:
                fp = StringIO()
                traceback.print_exc(file=fp)
                stack_trace_msg = fp.getvalue()
                logger.error(stack_trace_msg)
                send_exception_email(message.body, stack_trace_msg)
                logger.info("Exception email sent.")
