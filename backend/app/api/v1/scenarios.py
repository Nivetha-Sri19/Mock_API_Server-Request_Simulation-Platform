from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.enums import PermissionType, UserRole
from app.core.exceptions import NotFoundException
from app.core.redis import redis_client
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_database_session
from app.dependencies.permissions import check_api_permission
from app.models.user import User
from app.repositories.api_version_repository import APIVersionRepository
from app.repositories.mock_api_repository import MockAPIRepository
from app.schemas.response_template import (
    ResponseTemplateCreate,
    ResponseTemplateListResponse,
    ResponseTemplateResponse,
    ResponseTemplateUpdate,
)
from app.services.dynamic_endpoint_service import DynamicEndpointService
from app.services.scenario_service import ScenarioService


router = APIRouter(
    prefix="/mock-apis/{mock_api_id}/versions/{version_id}/scenarios",
    tags=["Response Scenarios"],
)


async def _get_version(
    mock_api_id: UUID,
    version_id: UUID,
    user: User,
    session: AsyncSession,
    manage: bool = False,
):
    mock_api_repository = MockAPIRepository(session)

    api = await mock_api_repository.get_by_id(mock_api_id)

    if api is None:
        raise NotFoundException(
            message="Mock API not found",
            error_code="MOCK_API_NOT_FOUND",
        )

    version_repository = APIVersionRepository(session)

    version = await version_repository.get_by_id_and_api(
        version_id,
        mock_api_id,
    )

    if version is None:
        raise NotFoundException(
            message="API version not found",
            error_code="API_VERSION_NOT_FOUND",
        )

    # Owner and admin have direct access.
    if user.role != UserRole.ADMIN and api.user_id != user.id:
        permission = (
            PermissionType.MANAGE
            if manage
            else PermissionType.VIEW
        )

        await check_api_permission(
            mock_api_id,
            user.id,
            permission,
            session,
        )

    return version


@router.post(
    "",
    response_model=ResponseTemplateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_scenario(
    mock_api_id: UUID,
    version_id: UUID,
    data: ResponseTemplateCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_database_session),
):
    await _get_version(
        mock_api_id,
        version_id,
        current_user,
        session,
        True,
    )

    service = ScenarioService(session)

    template = await service.create_scenario(
        version_id,
        data,
    )

    await session.commit()

    return template


@router.get(
    "",
    response_model=ResponseTemplateListResponse,
)
async def list_scenarios(
    mock_api_id: UUID,
    version_id: UUID,
    page: int = Query(
        1,
        ge=1,
    ),
    page_size: int = Query(
        20,
        ge=1,
        le=100,
    ),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_database_session),
):
    await _get_version(
        mock_api_id,
        version_id,
        current_user,
        session,
    )

    service = ScenarioService(session)

    items, total, total_pages = await service.list_scenarios(
        version_id,
        page=page,
        page_size=page_size,
    )

    return ResponseTemplateListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )


@router.get(
    "/{scenario_id}",
    response_model=ResponseTemplateResponse,
)
async def get_scenario(
    mock_api_id: UUID,
    version_id: UUID,
    scenario_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_database_session),
):
    await _get_version(
        mock_api_id,
        version_id,
        current_user,
        session,
    )

    service = ScenarioService(session)

    return await service.get_scenario(
        scenario_id,
        version_id,
    )


@router.patch(
    "/{scenario_id}",
    response_model=ResponseTemplateResponse,
)
async def update_scenario(
    mock_api_id: UUID,
    version_id: UUID,
    scenario_id: UUID,
    data: ResponseTemplateUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_database_session),
):
    await _get_version(
        mock_api_id,
        version_id,
        current_user,
        session,
        True,
    )

    service = ScenarioService(session)

    template = await service.update_scenario(
        scenario_id,
        version_id,
        data,
    )

    await session.commit()

    # Clear cached dynamic endpoint configuration.
    dynamic_service = DynamicEndpointService(
        session,
        redis_client,
    )

    await dynamic_service.invalidate(version_id)

    return template


@router.delete(
    "/{scenario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_scenario(
    mock_api_id: UUID,
    version_id: UUID,
    scenario_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_database_session),
):
    await _get_version(
        mock_api_id,
        version_id,
        current_user,
        session,
        True,
    )

    service = ScenarioService(session)

    await service.delete_scenario(
        scenario_id,
        version_id,
    )

    await session.commit()

    # Clear cached dynamic endpoint configuration.
    dynamic_service = DynamicEndpointService(
        session,
        redis_client,
    )

    await dynamic_service.invalidate(version_id)

    return None