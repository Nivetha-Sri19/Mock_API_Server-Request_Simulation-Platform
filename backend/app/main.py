from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as api_v1_router
from app.core.config import settings
from app.core.exception_handlers import (
    app_exception_handler,
    general_exception_handler,
    http_exception_handler,
    sqlalchemy_exception_handler,
    validation_exception_handler,
)
from app.core.exceptions import AppException
from app.core.logging import configure_logging
from app.core.redis import check_redis_connection, close_redis
from app.dynamic.router import dynamic_router
from app.middleware.request_context import RequestContextMiddleware
from app.middleware.request_logging import request_logging_middleware
from app.middleware.timing import timing_middleware


configure_logging(settings.LOG_LEVEL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_available = await check_redis_connection()

    if not redis_available:
        import logging

        logging.getLogger(__name__).warning(
            "Redis is unavailable. Application will continue without Redis cache.",
        )

    yield

    await close_redis()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Enterprise API Mock Server and Request Simulation Platform "
        "for creating, testing, versioning, and monitoring mock APIs."
    ),
    debug=settings.DEBUG,
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestContextMiddleware)

app.middleware("http")(request_logging_middleware)
app.middleware("http")(timing_middleware)


app.add_exception_handler(
    AppException,
    app_exception_handler,
)

app.add_exception_handler(
    422,
    validation_exception_handler,
)

app.add_exception_handler(
    500,
    general_exception_handler,
)

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError


app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.add_exception_handler(
    StarletteHTTPException,
    http_exception_handler,
)

app.add_exception_handler(
    SQLAlchemyError,
    sqlalchemy_exception_handler,
)


app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)
app.include_router(dynamic_router)


@app.get(
    "/",
    tags=["Health"],
)
async def root() -> dict[str, str]:
    return {
        "success": "true",
        "message": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get(
    "/health",
    tags=["Health"],
)
async def health_check() -> dict[str, object]:
    redis_available = await check_redis_connection()

    return {
        "status": "healthy",
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "redis": "up" if redis_available else "down",
    }