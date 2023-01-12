import numpy as np
import pandas as pd
import os
import tensorflow as tf

from app.utils.aws_utils import download_directory
from app.utils.constants import MODEL_SENTIMENT_TAGGING_DICT


def get_sentiment(data: pd.DataFrame, use_model):
    """
    Analyses comments in given dataframe and returns their sentiment and sentiment score.
    Args:
        data: data frame with single column containing text/comments
        use_model: Sentiment model

    Returns: a list containing sentiment (Positive, Negative or Neutral) for every comment in given dataframe and a
    list for their sentiment score.

    """
    prediction = use_model.predict(data)
    sentiment_score = np.amax(prediction, axis=-1)
    sentiment_code = np.argmax(prediction, axis=-1)
    sentiment_list = list(map(MODEL_SENTIMENT_TAGGING_DICT.get, sentiment_code))
    return sentiment_list, sentiment_score


def load_custom_model(model_path: str, model_bucket: str):
    """
    This function tries loading custom model from the given model_path if it exists, if not it first downloads it from
    aws from the given model_path and then loads it.
    Args:
        model_path: path of model in aws
        model_bucket: aws bucket name

    Returns: custom_model object

    """
    try:
        custom_model = tf.keras.models.load_model(model_path)
    except OSError or ImportError or IOError:
        download_directory(model_path, "", model_bucket)
        custom_model = tf.keras.models.load_model(model_path)

    return custom_model


if __name__ == "__main__":
    print(os.path.dirname("models/sentiment_model/v1"))
