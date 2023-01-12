from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    __model__ = None

    def __init__(self):
        pass

    # Functions
    @classmethod
    def _name(cls):
        """Returns a name of service class"""
        return cls.__name__

    @property
    def model_cls(self):
        """Returns a class of model which binds to the service"""
        return self.__model__

    def get_by_id(self, id: str, db: Session):
        return db.query(self.model_cls).filter(self.model_cls.id == id).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(self.model_cls).offset(skip).limit(limit).all()

    def create_or_update(self, db: Session, *, obj_in: CreateSchemaType):
        is_deleted_user_obj = db.query(self.model_cls).filter(self.model_cls.email == obj_in.email,
                                                              self.model_cls.is_deleted == True).first()
        if is_deleted_user_obj:
            return self.update(db_obj=is_deleted_user_obj, update_data={"is_deleted": False}, db=db)

        return self.create(db=db, obj_in=obj_in)

    def update(self, db_obj, update_data: dict, db: Session):
        obj_data = jsonable_encoder(db_obj)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model_cls(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        obj = db.query(self.model_cls).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def execute_raw_sql(self, query: str, db: Session):
        result = db.execute(query)
        response = [row for row in result]
        return response

    def execute_dml_raw_sql(self, query: str, db: Session):
        db.execute(query)
        db.commit()

