import email.utils
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from app.core import config
from app.core.config import logger


def send_email(subject, body_text, receiver_emails: list = None, files: list = None):
    email_list = receiver_emails if receiver_emails else config.RECIPIENT.split(",")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = email.utils.formataddr((config.SENDERNAME, config.SENDER))
    msg["To"] = ", ".join(receiver_emails) if receiver_emails else config.RECIPIENT

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(body_text, "plain")
    msg.attach(part1)

    if files:
        for path in files:
            part = MIMEBase("application", "octet-stream")
            with open(path, "rb") as file:
                part.set_payload(file.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                "attachment; filename={}".format("ClassificationResult.csv"),
            )
            msg.attach(part)

    try:
        server = smtplib.SMTP(config.HOST, config.PORT)
        server.ehlo()
        server.starttls()

        # stmplib docs recommend calling ehlo() before & after starttls()
        server.ehlo()
        server.login(config.USERNAME_SMTP, config.PASSWORD_SMTP)
        server.sendmail(config.SENDER, email_list, msg.as_string())
        server.close()
    except Exception as e:
        logger.error(f"Error sending email :- {e}")
