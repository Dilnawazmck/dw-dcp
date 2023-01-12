from typing import Callable

# from loguru import logger

from app.db.session import engine
from app.models import *
from app.models import Base
from app.services.data_ingestion.factory_data import insert_factory_data


def create_start_app_handler():
    def run_migrations() -> None:
        logger.info("Running migrations")
        Base.metadata.create_all(bind=engine)
        insert_factory_data()
    return run_migrations


#
# def create_stop_app_handler(app: FastAPI) -> Callable:  # type: ignore
#     @logger.catch
#     async def stop_app() -> None:
#         await close_db_connection(app)
#
#     return stop_app
