import time
import uuid
from threading import local

from django.db import connection
from loguru import logger


_thread_locals = local()


def get_request_id() -> str:
    return getattr(_thread_locals, "request_id", "N/A")


class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logger.patch(
            lambda record: record.update(request_id=get_request_id())
        )

    def __call__(self, request):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        _thread_locals.request_id = request_id
        request.request_id = request_id

        response = self.get_response(request)
        response["X-Request-ID"] = request_id
        return response

    def process_exception(self, request, exception):
        logger.opt(exception=exception).error(
            "Необработанное исключение {method} {path}",
            method=request.method,
            path=request.path,
        )


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(connection, 'queries'):
            connection.queries.clear()
        started_at = time.monotonic()

        response = self.get_response(request)
        duration = time.monotonic() - started_at

        sql_queries = getattr(connection, 'queries', [])
        sql_count = len(sql_queries)
        sql_time = sum(float(q.get('time', 0)) for q in sql_queries)

        if request.path.startswith('/api/v1/support/'):
            component = 'support'
        else:
            component = 'parcels'

        log = logger.bind(
            component=component,
            request_id=getattr(request, 'request_id', 'N/A'),
            method=request.method,
            path=request.path,
            status=response.status_code,
            duration_ms=round(duration * 1000, 2),
            sql_count=sql_count,
            sql_time_ms=round(sql_time * 1000, 2),
        )

        if response.status_code >= 500:
            log.error("Запрос завершен с ошибкой сервера")
        elif response.status_code >= 400:
            log.warning("Запрос завершен с ошибкой клиента")
        else:
            log.info("Запрос завершен")

        return response
