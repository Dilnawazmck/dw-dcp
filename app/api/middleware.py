import json
import logging
import time
import typing
from typing import Callable

from fastapi import FastAPI, Request, Response
from jose import jwt
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.encryption_utils import get_encrypted_string

#
# class async_iterator_wrapper:
#     def __init__(self, obj):
#         self._it = iter(obj)
#
#     def __aiter__(self):
#         return self
#
#     async def __anext__(self):
#         try:
#             value = next(self._it)
#         except StopIteration:
#             raise StopAsyncIteration
#         return value
#
#
# class RouteLoggerMiddleware(BaseHTTPMiddleware):
#     def __init__(
#         self,
#         app: FastAPI,
#         *,
#         logger: typing.Optional[logging.Logger] = None,
#     ):
#         self._logger = logger if logger else logging.getLogger(__name__)
#         super().__init__(app)
#
#     async def dispatch(self, request: Request, call_next: Callable) -> Response:
#         return await self._execute_request_with_logging(request, call_next)
#
#     async def _execute_request_with_logging(
#         self, request: Request, call_next: Callable
#     ) -> Response:
#         start_time = time.perf_counter()
#         try:
#             response = await self._execute_request(call_next, request)
#             # response.headers["X-Frame-Options"] = "deny"
#             # response.headers["X-Content-Type-Options"] = "nosniff"
#             # response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
#             # # response.headers["Content-Security-Policy"] = "default-src img-src 'self'"
#             # response.headers[
#             #     "Cache-Control"
#             # ] = "no-cache, no-store, max-age=0, must-revalidate"
#             # response.headers[
#             #     "Strict-Transport-Security"
#             # ] = "max-age=31536000; includeSubDomains"
#             # response.headers["X-XSS-Protection"] = "1; mode=block"
#         except Exception:
#             finish_time = time.perf_counter()
#             self._logger.error(
#                 self._generate_log(request, 500, finish_time - start_time)
#             )
#             raise
#         finish_time = time.perf_counter()
#         self._logger.info(
#             self._generate_log(request, response.status_code, finish_time - start_time)
#         )
#
#         return response
#
#     def _generate_log(self, request: Request, status_code: int, execution_time: float):
#         return self.get_logging_data(request, status_code, execution_time)
#
#     @staticmethod
#     def get_logging_data(request: Request, status_code: int, execution_time: float):
#         token = request.headers.get("Authorization")
#         encrypted_user_email = "NA"
#         if token:
#             try:
#                 decoded_data = jwt.get_unverified_claims(token.replace("Bearer ", ""))
#                 encrypted_user_email = get_encrypted_string(
#                     decoded_data.get("user", {}).get("email", "")
#                 )
#             except Exception:
#                 encrypted_user_email = "Unauthenticated"
#         return f"{encrypted_user_email} | {request.url} | {request.method} | {status_code} | {execution_time:0.4f}s"
#
#     @staticmethod
#     async def _execute_request(call_next: Callable, request: Request) -> Response:
#         response = await call_next(request)
#         return response
