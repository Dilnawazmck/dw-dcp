import json
import os
import tempfile
import traceback
from io import StringIO
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from app.core import config
from app.core.config import logger
from app.db.session import get_db_session
from app.models.nonohi_data import Nonohi_Data
from app.utils.aws_utils import (
    download_files,
    files_exist_in_bucket,
    get_all_keys,
    get_nested_file_paths,
    get_sqs_queue,
    upload_file_s3,
)
from app.utils.email_utils import send_email


def get_dataframe(file_path, sheet_name):
    df_input: pd.DataFrame = pd.read_excel(
        file_path, sheet_name=sheet_name, header=0, keep_default_na=False
    )
    return df_input


def transform_data(file_path, temp_base_folder, nonohi_pid):
    db: Session = next(get_db_session())
    nonohi_obj = db.query(Nonohi_Data).filter(Nonohi_Data.pid == nonohi_pid).first()

    df_input_data = get_dataframe(file_path, "data")
    df_data_column = get_dataframe(file_path, "metadata_column")
    df_filter_options = get_dataframe(file_path, "metadata_options")

    df_output_data = df_input_data
    df_output_data["responseid"] = range(1, len(df_output_data) + 1)

    final_metadata_dict = {
        "client_name": nonohi_obj.client_name,
        "survey_name": nonohi_obj.dataset_name,
        "survey_type": 4,
    }

    data_cols_name = df_data_column["data_column_name"]
    data_cols_text = df_data_column["data_column_text"]

    data_col_list = []

    for name, text in zip(data_cols_name, data_cols_text):
        temp_dict = {"column_name": name, "display_name": text, "type": 4}
        data_col_list.append(temp_dict)

    final_metadata_dict["data"] = data_col_list

    filter_cols_name = df_data_column["filter_column_name"]
    filter_cols_text = df_data_column["filter_column_text"]

    filter_cols_list = []

    for name, text in zip(filter_cols_name, filter_cols_text):
        temp_option_list = []
        temp_option_name_list = df_filter_options[name]
        temp_option_text_list = df_filter_options.iloc[
            :, (df_filter_options.columns.get_loc(name) + 1)
        ]

        if (
            temp_option_name_list[0].lower() != "name"
            and temp_option_text_list[0].lower() != "text"
        ):
            raise Exception(
                f"File transformation: Error occurred while creating metadata for {name}."
            )
        temp_option_name_list.pop(0)
        temp_option_text_list.pop(0)
        for n, t in zip(temp_option_name_list, temp_option_text_list):
            if len(n.strip()) > 0 or len(t.strip()) > 0:
                temp_option_dict = {"column_value": n, "display_name": t}
                temp_option_list.append(temp_option_dict)

        temp_dict = {
            "options": temp_option_list,
            "column_name": name,
            "display_name": text,
        }
        filter_cols_list.append(temp_dict)

    final_metadata_dict["filters"] = filter_cols_list

    local_metadata_file_path = os.path.join(
        Path(temp_base_folder.name), config.S3_METADATAFILE
    )
    local_data_file_path = os.path.join(Path(temp_base_folder.name), config.S3_DATAFILE)

    with open(local_metadata_file_path, "w") as outfile:
        json.dump(final_metadata_dict, outfile)

    df_output_data.to_csv(local_data_file_path, index=False)

    s3_metadata_file_path = os.path.join(Path(nonohi_pid), config.S3_METADATAFILE)
    s3_data_file_path = os.path.join(Path(nonohi_pid), config.S3_DATAFILE)

    return (
        local_metadata_file_path,
        local_data_file_path,
        s3_metadata_file_path,
        s3_data_file_path,
    )


def process_message(message_body):
    for record in message_body["Records"]:
        s3_keys = get_all_keys(record)

        if not s3_keys["bucket"] or not s3_keys["folder"]:
            raise Exception(
                "File transformation: Invalid message received. Bucket/folder key not present in the message."
            )

        temp_base_folder = tempfile.TemporaryDirectory(s3_keys["folder"])

        s3_input_file_path = get_nested_file_paths(s3_keys["folder"], [s3_keys["file"]])

        data_file_path = [os.path.join(Path(temp_base_folder.name), s3_keys["file"])]

        files_exist_in_bucket(s3_keys["bucket"], s3_input_file_path)

        download_files(s3_keys["bucket"], s3_input_file_path, data_file_path)
        (
            local_metadata_file_path,
            local_data_file_path,
            s3_metadata_file_path,
            s3_data_file_path,
        ) = transform_data(data_file_path[0], temp_base_folder, s3_keys["folder"])

        upload_file_s3(
            local_metadata_file_path, config.AWS_BUCKET, s3_metadata_file_path
        )

        upload_file_s3(local_data_file_path, config.AWS_BUCKET, s3_data_file_path)

        return s3_keys["folder"]


def send_email_etl(p_id):
    subject = "Text Analytics:- File transformation successfully completed!"
    body_text = f"Hi,\n\nFile transformation for project {p_id} successfully completed! File has been sent for NLP processing."
    send_email(subject, body_text)


def send_exception_email(queue_msg, stack_trace):
    subject = "Text Analytics[ERROR] File transformation"
    body_text = (
        f"Hi,\n\nError occurred for below project."
        f"\n\nQueue Message:-\n{queue_msg}"
        f"\n\nstack trace:-\n{stack_trace}"
    )
    send_email(subject, body_text)


if __name__ == "__main__":
    # transform_data("tmp/test.xlsx", "tmp", "nop1")
    while True:
        messages = get_sqs_queue(config.SQS_QUEUE_NON_OHI).receive_messages()

        for message in messages:
            logger.info("File transformation: message received")
            logger.info(message.body)
            try:
                json_obj = json.loads(message.body)
                message.delete()
                logger.info(
                    "File transformation: Message deleted from queue and processing starts."
                )
                project_id = process_message(json_obj)
                send_email_etl(project_id)
                logger.info("File transformation: Success email sent.")
            except Exception:
                fp = StringIO()
                traceback.print_exc(file=fp)
                stack_trace_msg = fp.getvalue()
                logger.error(stack_trace_msg)
                send_exception_email(message.body, stack_trace_msg)
                logger.info(
                    "File transformation: Exception email sent while transforming file."
                )
