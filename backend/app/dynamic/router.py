import logging
from time import perf_counter
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.enums import PermissionType, UserRole
from app.core.exceptions import (
    AuthenticationException,
    AuthorizationException,
)
from app.core.redis import redis_client
from app.core.security import decode_access_token
from app.dependencies.database import get_database_session
from app.dynamic.executor import DynamicEndpointExecutor
from app.dynamic.matcher import EndpointMatcher
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.dynamic_endpoint_service import DynamicEndpointService
from app.services.permission_service import PermissionService


logger = logging.getLogger(__name__)


dynamic_router = APIRouter(
    prefix="/mock",
    tags=["Dynamic Mock APIs"],
)

executor = DynamicEndpointExecutor()


async def _get_optional_user(
    request: Request,
    session: AsyncSession,
) -> User | None:

    header = request.headers.get(
        "authorization",
        "",
    )

    if not header:
        return None

    scheme, _, token = header.partition(" ")

    if scheme.lower() != "bearer" or not token:
        raise AuthenticationException(
            error_code="INVALID_AUTHORIZATION_HEADER",
        )

    try:
        payload = decode_access_token(token)

        user_id = UUID(
            str(payload["sub"]),
        )

    except (ValueError, KeyError, TypeError):
        raise AuthenticationException(
            error_code="INVALID_ACCESS_TOKEN",
        )

    user = await UserRepository(
        session,
    ).get_active_by_id(user_id)

    if user is None:
        raise AuthenticationException(
            error_code="USER_NOT_FOUND",
        )

    return user


def _runtime_path(
    request: Request,
) -> str:

    path = request.url.path.strip()

    if not path:
        return "/"

    if path == "/mock":
        return "/"

    if path.startswith("/mock/"):
        path = path[len("/mock"):]

    if not path.startswith("/"):
        path = f"/{path}"

    return path


async def handle_dynamic_request(
    request: Request,
    session: AsyncSession,
) -> Response:

    service = DynamicEndpointService(
        session=session,
        redis_client=redis_client,
    )

    definitions = await service.find_matching_definitions(
        method=request.method,
    )

    runtime_path = _runtime_path(
        request,
    )

    logger.info(
        "Dynamic request: method=%s "
        "request_path=%s "
        "runtime_path=%s "
        "definitions=%s",
        request.method,
        request.url.path,
        runtime_path,
        len(definitions),
    )

    matched = EndpointMatcher(
        definitions,
    ).match(
        method=request.method,
        path=runtime_path,
    )

    definition = await service.get_definition(
        matched.api_version_id,
    )

    if definition is None:
        raise AuthorizationException(
            message="Mock API is inactive",
            error_code="MOCK_API_INACTIVE",
        )

    if definition.get("is_private"):
        user = await _get_optional_user(
            request,
            session,
        )

        if user is None:
            raise AuthenticationException(
                message=(
                    "Authentication required "
                    "for this private mock API"
                ),
            )

        if (
            user.role != UserRole.ADMIN
            and user.id != matched.owner_id
        ):
            await PermissionService(
                session,
            ).require_permission(
                mock_api_id=matched.api_id,
                user_id=user.id,
                permission=PermissionType.EXECUTE,
            )

    scenario = request.query_params.get(
        "__scenario",
    )

    started = perf_counter()

    response = await executor.execute(
        request=request,
        definition=definition,
        path_parameters=matched.path_parameters,
        scenario=scenario,
        session=session,
    )

    response.headers.setdefault(
        "X-Mock-API-Version",
        matched.version,
    )

    response.headers.setdefault(
        "X-Request-Processing-ms",
        f"{(perf_counter() - started) * 1000:.2f}",
    )

    return response


@dynamic_router.api_route(
    "/{full_path:path}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "HEAD",
        "OPTIONS",
    ],
    include_in_schema=False,
)
async def dynamic_endpoint(
    full_path: str,
    request: Request,
    session: AsyncSession = Depends(
        get_database_session,
    ),
) -> Response:

    return await handle_dynamic_request(
        request=request,
        session=session,
    )


def register_dynamic_routes(
    app: Any,
    definitions: list[dict[str, Any]],
) -> None:

    logger.info(
        "Dynamic routes use the catch-all "
        "/mock/{full_path:path} router; "
        "no route registration is required.",
    )