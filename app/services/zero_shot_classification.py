from datetime import datetime

import pandas as pd
from fastapi import BackgroundTasks
from transformers import pipeline

from app.core.config import logger
from app.services.base_service import BaseService
from app.utils import email_utils

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")


class ZeroShotClassificationService(BaseService):
    def __init__(self):
        super().__init__()

    @staticmethod
    def _get_pipeline_response(text: list, labels: list):
        result = classifier(text, labels)
        return result

    @staticmethod
    def create_output_csv(data: list):
        output_list = []
        output_csv_path = "/tmp/ClassificationResult{}.csv".format(str(datetime.now()))
        for item in data:
            output_list.append(
                [
                    item["sequence"],
                    item["labels"][0],
                    str(round(item["scores"][0] * 100, 1)) + "%",
                ]
            )
        df = pd.DataFrame(output_list, columns=["text", "label", "score"])
        df.to_csv(output_csv_path, index=False)
        return output_csv_path

    def process_zero_shot_classification_in_background(
        self, text: list, labels: list, user_email: str
    ):
        result = self._get_pipeline_response(text=text, labels=labels)
        output_csv_path = self.create_output_csv(result)
        email_utils.send_email(
            subject="Text Analytics Classification Result",
            body_text="Here is the classification result.",
            receiver_emails=[user_email],
            files=[output_csv_path],
        )
        logger.info("Email sent to {}".format(user_email))

    def get_most_relevant_label(
        self,
        text: list,
        labels: list,
        user_email: str,
        background_tasks: BackgroundTasks,
    ):
        """
        Uses transformer classifier to find the most similar label for the provided text. If there are multiple
        comments that needs to be tagged, it creates a background task for it and send it as an email attachment to the
        logged in user.

        Args:
            text (list): List of comments that need to be labelled
            labels (list): Labels to be used for classification.
            user_email(str): Email of the user
            background_tasks (starlette.background.BackgroundTasks): Background task to be used for multiple comments
        Returns:
            dict: If len(text)>1 it triggers an email else a dict containing the text with the most similar label

        Raises:
            N/A

        Examples:
            >>> get_most_relevant_label(["I am the king"], \
                                        ["food","palace","animals","love"], \
                                        "abc@mckinsey.com", background_tasks)
            {
              "sequence": "I am the king",
              "labels": [
                "palace",
                "love",
                "animals",
                "food"
              ],
              "scores": [
                0.9039514660835266,
                0.036746032536029816,
                0.036745648831129074,
                0.022556796669960022
              ]
            }
        """
        if len(text) > 1:
            background_tasks.add_task(
                self.process_zero_shot_classification_in_background,
                text,
                labels,
                user_email,
            )
            estimated_time = (
                "60 seconds"
                if len(text) <= 60
                else str(round(len(text) / 60, 2)) + " minutes"
            )
            message = (
                "Report will be sent to your email id within {estimated_time}".format(
                    estimated_time=estimated_time
                )
            )
            return {
                "status": "Success",
                "estimated_time": estimated_time,
                "message": message,
            }
        result = self._get_pipeline_response(text=text, labels=labels)
        return result


_zero_shot_service = ZeroShotClassificationService()
