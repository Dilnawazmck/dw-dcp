from app.models.sentiment import Sentiment
from app.services.base_service import BaseService


class SentimentServices(BaseService):
    __model__ = Sentiment

    @property
    def model_cls(self):
        """Returns a class of model which binds to the service"""
        return self.__model__

    def sentiment_score(self, positive: int, negative: int):
        if positive + negative:
            response = round(((positive - negative) / (positive + negative)) * 100)
        else:
            response = 0

        return response


_sentiment = SentimentServices()
