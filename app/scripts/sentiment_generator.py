import traceback
from io import StringIO

import pandas as pd
import tensorflow_text as text
from sqlalchemy.orm import Session

from app.core import config
from app.core.logging import logger
from app.db.session import get_db_session
from app.models.response import Response
from app.services.sentiment import _sentiment
from app.services.sentiment_analysis import get_sentiment, load_custom_model
from app.utils.email_utils import send_email

EMAIL_LIST = config.SENTIMENT_EMAIL_RECIPIENTS.split(",")

SENTIMENT_MODEL = load_custom_model(
    model_path=config.SENTIMENT_MODEL_PATH, model_bucket=config.AWS_BUCKET
)

CHUNK_SIZE = config.DATA_CHUNK_SIZE


def fetch_chunk_from_db(db: Session):
    response = (
        db.query(Response.id, Response.answer)
        .filter(Response.sentiment_id.is_(None))
        .limit(CHUNK_SIZE)
        .all()
    )
    return response


def get_sentiment_metadata(db_session: Session):
    sentiments = _sentiment.get_all(db_session)
    sentiment_dict = {sentiment.name: sentiment.id for sentiment in sentiments}
    return sentiment_dict


def send_exception_email(stack_trace):
    subject = "Text Analytics[ERROR]"
    body_text = (
        f"Hi,\n\nError occurred for below project." f"\n\nstack trace:-\n{stack_trace}"
    )
    send_email(subject, body_text, EMAIL_LIST)


def process_data(data, db_session: Session):
    # x = input_data[1]
    df_input = pd.DataFrame(data=data, columns=["id", "answer"])
    sentiment_dict = get_sentiment_metadata(db_session)
    logger.info(f"dataframe length {len(df_input)}")
    logger.info("Sentiment tagging started")
    sentiment_list, sentiment_score_list = get_sentiment(
        df_input["answer"], SENTIMENT_MODEL
    )
    df_input["sentiment_id"] = [
        sentiment_dict[sentiment] for sentiment in sentiment_list
    ]
    df_input["sentiment_score"] = sentiment_score_list
    logger.info("Tagging ends")
    update_list = df_input[["id", "sentiment_id", "sentiment_score"]].to_dict("records")

    logger.info("update started")
    db_session.bulk_update_mappings(Response, update_list)
    db_session.commit()
    logger.info("commit done!")


if __name__ == "__main__":
    db: Session = next(get_db_session())
    logger.info("Sentiment processing begins. Db session created!")
    while True:
        try:
            input_data = fetch_chunk_from_db(db)
            logger.info("data fetched")
            if not input_data:
                # send_completion_email()
                logger.info("Processing done! Exiting! sending success email")
                send_email(
                    "Sentiment processing completed",
                    "Sentiment processing is completed!",
                    EMAIL_LIST,
                )
                break
            process_data(input_data, db)
        except Exception:
            fp = StringIO()
            traceback.print_exc(file=fp)
            stack_trace_msg = fp.getvalue()
            logger.error(stack_trace_msg)
            send_exception_email(stack_trace_msg)
            logger.info("Exception email sent.")
