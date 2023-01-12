import logging
from typing import List

# from loguru import logger
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings, Secret

from app.core.logging import InterceptHandler

VERSION = "0.0.0"

config = Config(".env")

API_PREFIX = "/api"
DEBUG: bool = config("DEBUG", cast=bool, default=False)
ENV: str = config("ENV", default="local")
SECRET_KEY: str = config("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = config(
    "ACCESS_TOKEN_EXPIRE_MINUTES", cast=int, default=30
)
REFRESH_TOKEN_EXPIRE_MINUTES: int = config(
    "REFRESH_TOKEN_EXPIRE_MINUTES", cast=int, default=1440
)
PROJECT_NAME: str = config("PROJECT_NAME", default="dw-dcp")

ALLOWED_HOSTS: List[str] = config(
    "ALLOWED_HOSTS",
    cast=CommaSeparatedStrings,
    default="",
)
#
# SQLALCHEMY_DATABASE_URI: str = config("SQLALCHEMY_DATABASE_URI")
# TEST_DATABASE_URI: str = config("TEST_DATABASE_URI")
#
# HASH_SALT: str = config("SECRET_KEY")
# HASH_MIN_LENGTH: int = 4
#
# CRYPT_KEY: str = config("CRYPT_KEY")
#
# AWS_ACCESS_KEY: str = config("AWS_ACCESS_KEY")
# AWS_SECRET_KEY: str = config("AWS_SECRET_KEY")
# AWS_REGION: str = config("AWS_REGION")

# logging configuration
# LOGGING_LEVEL = logging.DEBUG
# LOGGERS = ("uvicorn.asgi", "uvicorn.access")
#
# logging.getLogger().handlers = [InterceptHandler()]
# for logger_name in LOGGERS:
#     logging_logger = logging.getLogger(logger_name)
#     logging_logger.handlers = [InterceptHandler(level=LOGGING_LEVEL)]
#
# logger.configure(handlers=[{"sink": "log/text_analytics.log", "level": LOGGING_LEVEL}])

# SQS_QUEUE: str = config("SQS_QUEUE")
# S3_DATAFILE: str = "data.csv"
# S3_METADATAFILE: str = "metadata.json"
#
# DATA_CHUNK_SIZE: int = 200
#
# SENDER: str = config("SENDER")
# SENDERNAME = config("SENDERNAME")
# RECIPIENT = config("RECIPIENT")
# USERNAME_SMTP = config("USERNAME_SMTP")
# PASSWORD_SMTP = config("PASSWORD_SMTP")
# HOST = config("HOST")
# PORT = config("PORT")
#
# MCKID_USERINFO_URL: str = config("MCKID_USERINFO_URL")
#
# TEST_TOKEN_AUTH_ACCESS: str = config("TEST_TOKEN_AUTH_ACCESS")
# TEST_TOKEN_CLIENT_LIST: str = config("TEST_TOKEN_CLIENT_LIST")
# TEST_DUMMY_TOKEN: str = config("TEST_DUMMY_TOKEN")
#
# REDIS_URI: str = config("REDIS_URI")
# CHUNK_PROCESSING_TIME: int = int(config("CHUNK_PROCESSING_TIME"))
# APP_DOMAIN_URL: str = config("APP_DOMAIN_URL")
#
# AWS_BUCKET: str = config("AWS_BUCKET")
# SENTIMENT_MODEL_PATH: str = config("SENTIMENT_MODEL_PATH")
#
# SQS_QUEUE_NON_OHI: str = config("SQS_QUEUE_NON_OHI")
#
# AWS_BUCKET_NON_OHI_UPLOAD_API: str = config("AWS_BUCKET_NON_OHI_UPLOAD_API")
# AWS_BUCKET_TRANSFORM: str = config("AWS_BUCKET_TRANSFORM")
#
# SENTIMENT_EMAIL_RECIPIENTS: str = config("SENTIMENT_EMAIL_RECIPIENTS")
