import os
from urllib.parse import unquote_plus

import boto3
import botocore
from botocore.exceptions import ClientError, NoCredentialsError

from app.core import config
from app.utils.encryption_utils import get_decrypted_string


def get_sqs_queue(queue_name):
    sqs = boto3.resource(
        "sqs",
        aws_access_key_id=get_decrypted_string(config.AWS_ACCESS_KEY),
        aws_secret_access_key=get_decrypted_string(config.AWS_SECRET_KEY),
        region_name=config.AWS_REGION,
    )
    queue = sqs.get_queue_by_name(QueueName=queue_name)
    return queue


def get_s3_resource():
    s3_resource = boto3.resource(
        "s3",
        aws_access_key_id=get_decrypted_string(config.AWS_ACCESS_KEY),
        aws_secret_access_key=get_decrypted_string(config.AWS_SECRET_KEY),
        region_name=config.AWS_REGION,
    )
    return s3_resource


def get_s3_client():
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=get_decrypted_string(config.AWS_ACCESS_KEY),
        aws_secret_access_key=get_decrypted_string(config.AWS_SECRET_KEY),
        region_name=config.AWS_REGION,
    )
    return s3_client


def download_files(bucket_name, file_objs, download_path):
    s3 = get_s3_resource()
    for f, d in zip(file_objs, download_path):
        s3.Bucket(bucket_name).download_file(f, d)


def files_exist_in_bucket(bucket, file_objs):
    s3 = get_s3_resource()
    if not file_objs:
        return False

    for f in file_objs:
        try:
            s3.Object(bucket, f).load()
        except botocore.exceptions.ClientError:
            raise Exception("Error occurred while checking, files exits in bucket.")

    return True


def download_directory(prefix, local, bucket):
    """

    Args:
        prefix: pattern to match in s3
        local: local path to folder in which to place files
        bucket: s3 bucket with target contents

    Returns:

    """
    client = get_s3_client()
    keys = []
    dirs = []
    next_token = ""
    base_kwargs = {
        "Bucket": bucket,
        "Prefix": prefix,
    }
    while next_token is not None:
        kwargs = base_kwargs.copy()
        if next_token != "":
            kwargs.update({"ContinuationToken": next_token})
        results = client.list_objects_v2(**kwargs)
        contents = results.get("Contents")
        for i in contents:
            k = i.get("Key")
            if k[-1] != "/":
                keys.append(k)
            else:
                dirs.append(k)
        next_token = results.get("NextContinuationToken")
    for d in dirs:
        dest_pathname = os.path.join(local, d)
        if not os.path.exists(os.path.dirname(dest_pathname)):
            os.makedirs(os.path.dirname(dest_pathname))
    for k in keys:
        dest_pathname = os.path.join(local, k)
        if not os.path.exists(os.path.dirname(dest_pathname)):
            os.makedirs(os.path.dirname(dest_pathname))
        client.download_file(bucket, k, dest_pathname)


def get_nested_key(input_dict, nested_key):
    # input_dic --> input dictionary
    # nested_key --> list of keys
    internal_dict_value = input_dict
    for k in nested_key:
        internal_dict_value = internal_dict_value.get(k, None)
        if internal_dict_value is None:
            return None
    return internal_dict_value


def get_all_keys(record):
    bucket = get_nested_key(record, ["s3", "bucket", "name"])
    folder = unquote_plus(get_nested_key(record, ["s3", "object", "key"])).split("/")[0]
    file = unquote_plus(get_nested_key(record, ["s3", "object", "key"])).split("/")[1]
    temp_dict = {"bucket": bucket, "folder": folder, "file": file}
    return temp_dict


def get_nested_file_paths(base_path, file_names):
    temp_file_path_list = []
    if not file_names or not base_path:
        return None
    for f in file_names:
        temp_file_path_list.append("{}/{}".format(base_path, f))
    return temp_file_path_list


def upload_file_s3(local_path, bucket, s3_path):
    """

    Args:
        local_path: file path in local machine
        bucket: s3 bucket where file needs to be uploaded
        s3_path: s3 path of the file

    Returns: True if file is successfully uploaded else raises eception

    """
    client = get_s3_client()
    try:
        client.upload_file(local_path, bucket, s3_path)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        raise Exception("The file was not found")
    except NoCredentialsError:
        print("Credentials not available")
        raise Exception("Credentials not available")


def copy_file(copy_source, destination_bucket, destination_file_path):
    """

    Args:
        copy_source: e.g copy_source = {
                                        'Bucket': 'mybucket',
                                        'Key': 'mykey'
                                    }
        destination_bucket: Bucket name where file needs to be copied
        destination_file_path: destination file path

    Returns:

    """

    client = get_s3_client()
    client.copy(copy_source, destination_bucket, destination_file_path)
    pass
