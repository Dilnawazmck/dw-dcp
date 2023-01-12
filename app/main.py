import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware

from app.api.errors.http_error import http_error_handler
from app.api.errors.validation_error import http422_error_handler
# from app.api.middleware import RouteLoggerMiddleware
from app.api.routes.api import router as api_router
from app.core.config import (
    ALLOWED_HOSTS,
    API_PREFIX,
    DEBUG,
    PROJECT_NAME,
    VERSION,
    # logger,
    ENV
)
# from app.core.events import create_start_app_handler


def get_application() -> FastAPI:
    application = FastAPI(
        title=PROJECT_NAME,
        debug=DEBUG,
        version=VERSION,
        openapi_url="/api/openapi.json" if ENV in ('local', 'dev') else None,
        docs_url="/api/docs" if ENV in ('local', 'dev') else None,
        redoc_url="/api/redoc" if ENV in ('local', 'dev') else None,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_HOSTS or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # application.add_event_handler("startup", create_start_app_handler())

    # application.add_exception_handler(HTTPException, http_error_handler)
    # application.add_exception_handler(RequestValidationError, http422_error_handler)
    application.include_router(api_router, prefix=API_PREFIX)
    return application


app = get_application()
# app.add_middleware(RouteLoggerMiddleware, logger=logger)

if __name__ == "__main__":
    uvicorn.run(
        app, host="127.0.0.1", port=8000, headers=[("server", "dw-dcp")]
    )
