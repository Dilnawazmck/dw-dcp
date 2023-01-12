import logging
import smtplib
from email.message import EmailMessage
from types import FrameType
from typing import cast

# from loguru import logger

from app.core import config


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # noqa: WPS609
            frame = cast(FrameType, frame.f_back)
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


# async def custom_sink(message):
#     msg = EmailMessage()
#     msg.set_content(message)
#     msg['Subject'] = 'Analytics Error on {} environment'.format(config.ENV)
#     msg['From'] = config.SENDER_EMAIL
#     msg['To'] = config.RECEIVER_EMAIL
#
#     with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as smtp_server:
#         smtp_server.login(config.SENDER_EMAIL, config.SMTP_PASSWORD)
#         smtp_server.send_message(msg)
#
#
# def error_only(record):
#     return record["level"].name == "ERROR"
