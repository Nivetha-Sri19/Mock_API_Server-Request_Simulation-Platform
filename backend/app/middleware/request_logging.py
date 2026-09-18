import logging
import time

from fastapi import Request


logger = logging.getLogger(__name__)


async def request_logging_middleware(
    request: Request,
    call_next,
):
    start_time = time.perf_counter()

    response = None

    try:
        response = await call_next(request)
        return response
    finally:
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        request_id = getattr(
            request.state,
            "request_id",
            "-",
        )

        status_code = (
            response.status_code
            if response is not None
            else 500
        )

        logger.info(
            "%s %s | status=%s | duration_ms=%.2f | request_id=%s",
            request.method,
            request.url.path,
            status_code,
            elapsed_ms,
            request_id,
        )