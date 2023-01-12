import io
import os
import tempfile
from pathlib import Path

import pandas as pd
from fastapi import UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.models.nonohi_data import Nonohi_Data
from app.services.base_service import BaseService


class NonohiDataService(BaseService):
    __model__ = Nonohi_Data

    @property
    def model_cls(self):
        """Returns a class of models which binds to the service"""
        return self.__model__

    @staticmethod
    def get_dataframe(file_path, sheet_name):
        try:
            df_input: pd.DataFrame = pd.read_excel(
                file_path, sheet_name=sheet_name, header=0
            )
        except Exception:
            raise Exception
        return df_input

    def get_all_order_by(self, db: Session, skip: int = 0, limit: int = 100):
        return (
            db.query(self.model_cls)
            .order_by(self.model_cls.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def validate_file(self, file_path: str):
        df_data = self.get_dataframe(file_path, "data")
        df_metadata = self.get_dataframe(file_path, "metadata_column")
        df_options = self.get_dataframe(file_path, "metadata_options")

        if not len(df_data.columns) == len(df_metadata["data_column_name"]) + len(
            df_metadata["data_column_text"]
        ):
            raise Exception("Columns mismatch in data sheet vs metadata_column sheet.")

        if not (len(df_data) > 0 and len(df_metadata) > 0 and len(df_options) > 1):
            raise Exception("Missing data in required sheets.")

        if len(df_metadata["filter_column_name"]) == len(df_options.columns):
            raise Exception(
                "Columns mismatch in metadata_column sheet vs metadata_options sheet."
            )

    def get_file_stream(self, file_path: str, file_name: str):
        df_Instructions = self.get_dataframe(file_path, "Instructions")
        df_data = self.get_dataframe(file_path, "data")
        df_metadata = self.get_dataframe(file_path, "metadata_column")
        df_options = self.get_dataframe(file_path, "metadata_options")

        stream = io.BytesIO()
        writer = pd.ExcelWriter(stream, engine="xlsxwriter")

        df_Instructions.to_excel(writer, sheet_name="Instructions", index=False)
        df_data.to_excel(writer, sheet_name="data", index=False)
        df_metadata.to_excel(writer, sheet_name="metadata_column", index=False)
        df_options.to_excel(writer, sheet_name="metadata_options", index=False)

        writer.save()
        response = StreamingResponse(iter([stream.getvalue()]))
        response.headers["Content-Disposition"] = "attachment; filename=" + file_name

        return response


_nonohi_data = NonohiDataService()
