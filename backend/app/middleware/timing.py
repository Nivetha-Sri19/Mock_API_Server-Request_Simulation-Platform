import time

from fastapi import Request


async def timing_middleware(
    request: Request,
    call_next,
):
    start_time = time.perf_counter()

    response = await call_next(request)

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    response.headers["X-Response-Time-ms"] = f"{elapsed_ms:.2f}"

    return response