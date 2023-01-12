from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.models.user_survey_preset import UserSurveyPreset
from app.schemas.user_survey_preset import UserSurveyPresetIn
from app.services.base_service import BaseService
from app.utils.app_utils import _hash


class UserSurveyPresetService(BaseService):
    __model__ = UserSurveyPreset

    @property
    def model_cls(self):
        """Returns a class of model which binds to the service"""
        return self.__model__

    def create_user_survey_preset(
        self, survey_id: str, name: str, user_id: int, preset_filters: List, survey_type: int, db: Session
    ) -> UserSurveyPreset:
        decoded_survey_id = _hash.decode(survey_id)
        if not decoded_survey_id:
            return None

        user_preset_obj = (
            db.query(self.model_cls)
            .filter(
                self.model_cls.user_id == user_id,
                self.model_cls.survey_id == decoded_survey_id[0],
                self.model_cls.name == name,
                self.model_cls.type == survey_type
            )
            .first()
        )

        if user_preset_obj:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Entry already exists"
            )
        obj_in = UserSurveyPresetIn(
            preset_filters=preset_filters,
            survey_id=decoded_survey_id[0],
            user_id=user_id,
            name=name,
            type=survey_type

        )

        self.create(db=db, obj_in=obj_in)

    def verify_user_preset_survey(
        self, user_id: int, preset_id: int, db: Session
    ) -> UserSurveyPreset:
        user_preset_obj = (
            db.query(self.model_cls)
            .filter(self.model_cls.user_id == user_id, self.model_cls.id == preset_id)
            .first()
        )
        if not user_preset_obj:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Entry does not exists"
            )
        return user_preset_obj

    def get_user_survey_preset(
        self, survey_id: str, user_id: int,survey_type: int, db: Session,
    ) -> UserSurveyPreset:
        decoded_survey_id = _hash.decode(survey_id)
        user_preset_obj = (
            db.query(
                self.model_cls.name, self.model_cls.preset_filters, self.model_cls.id, self.model_cls.type
            )
            .filter(
                self.model_cls.user_id == user_id,
                self.model_cls.survey_id == decoded_survey_id[0],
                self.model_cls.type == survey_type
            )
            .all()
        )

        # if not user_preset_obj:
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail="Entry does not exists"
        #     )

        return user_preset_obj


_preset = UserSurveyPresetService()
