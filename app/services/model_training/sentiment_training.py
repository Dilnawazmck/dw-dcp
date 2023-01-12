import tensorflow_hub as hub
import tensorflow as tf
import tensorflow_text as text
import numpy as np
import pandas as pd
from sklearn import model_selection
from tensorflow.keras import layers
from app.utils.constants import MODEL_SENTIMENT_TAGGING_DICT

#{0 - Negative, 1 - Neutral, 2 - Positive}


def train_model():
    train_df = pd.read_csv('tmp/train_data02.csv', sep=',')
    print(train_df.head())

    train_indices, validation_indices = model_selection.train_test_split(
        np.unique(train_df["id"]),
        test_size=0.1,
        random_state=0)

    validation_df = train_df[train_df["id"].isin(validation_indices)]
    train_df = train_df[train_df["id"].isin(train_indices)]
    print(len(train_df))
    print(len(validation_df))

    sentence_encoder_layer = hub.KerasLayer("https://tfhub.dev/google/universal-sentence-encoder-multilingual-large/3",
                                            input_shape=[],
                                            dtype=tf.string,
                                            trainable=False)
    model_1 = None
    model_1 = tf.keras.Sequential([
        sentence_encoder_layer,
        layers.Dense(128, activation="relu"),
        layers.Dense(3, activation="softmax")
    ], name="model_1_USE")

    print(model_1.summary())

    model_1.compile(loss='sparse_categorical_crossentropy',
                    optimizer=tf.keras.optimizers.Adam(),
                    metrics=["accuracy"])

    history = model_1.fit(x=train_df['Text'], y=train_df['sentiment'],
                          validation_data=(validation_df['Text'], validation_df['sentiment']),
                          epochs=7)

    model_1.save('tmp/sentiment_model_v2')


def predict_sentiment():
    new_model = tf.keras.models.load_model('tmp/sentiment_model_v1')
    tmp_df = pd.read_excel("tmp/Comments file.xlsx")
    test_df = pd.DataFrame()
    test_df['answer'] = tmp_df['Comments']
    pred = new_model.predict(test_df['answer'])
    test_predictions = np.argmax(pred, axis=-1)
    sentiment_list = list(map(MODEL_SENTIMENT_TAGGING_DICT.get, test_predictions))
    test_df["sentiment"] = sentiment_list

    test_df.to_excel("tmp/sentiment.xlsx")
    print(test_df.head())
    # print(result_df.head())


if __name__ == "__main__":
    train_model()
    # predict_sentiment()
