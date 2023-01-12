from sqlalchemy import Boolean, Column, DateTime, Integer
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.sql import func


@as_declarative()
class Base:
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True, autoincrement=True)

    last_updated_on = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    created_on = Column(DateTime, nullable=False, default=func.now())

    is_deleted = Column(Boolean, nullable=False, default=False)


# class BaseModel:
#     id = Column(
#         Integer,
#         primary_key=True,
#         autoincrement=True
#     )
#
#     last_updated_on = Column(
#         DateTime,
#         nullable=False,
#         default=func.utcnow(),
#         onupdate=func.utcnow()
#     )
#
#     created_on = Column(
#         DateTime,
#         nullable=False,
#         default=func.utcnow()
#     )
#
#     is_deleted = Column(
#         Boolean,
#         nullable=False,
#         default=False
#     )
