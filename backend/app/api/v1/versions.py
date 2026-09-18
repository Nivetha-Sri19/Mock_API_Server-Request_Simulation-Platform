from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.enums import PermissionType, UserRole
from app.core.exceptions import AuthorizationException
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_database_session
from app.dependencies.permissions import check_api_permission
from app.models.user import User
from app.repositories.mock_api_repository import MockAPIRepository
from app.schemas.api_version import APIVersionCreate, APIVersionListResponse, APIVersionResponse, APIVersionUpdate
from app.services.api_version_service import APIVersionService
from app.services.dynamic_endpoint_service import DynamicEndpointService
from app.core.redis import redis_client

router = APIRouter(prefix="/mock-apis/{mock_api_id}/versions", tags=["API Versions"])


async def _get_api(mock_api_id: UUID, current_user: User, session: AsyncSession):
    api = await MockAPIRepository(session).get_by_id(mock_api_id)
    if api is None:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(message="Mock API not found", error_code="MOCK_API_NOT_FOUND")
    if current_user.role != UserRole.ADMIN and api.user_id != current_user.id:
        await check_api_permission(mock_api_id, current_user.id, PermissionType.VIEW, session)
    return api


async def _ensure_manage_access(mock_api_id: UUID, current_user: User, session: AsyncSession):
    api = await MockAPIRepository(session).get_by_id(mock_api_id)
    if api is None:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(message="Mock API not found", error_code="MOCK_API_NOT_FOUND")
    if current_user.role != UserRole.ADMIN and api.user_id != current_user.id:
        await check_api_permission(mock_api_id, current_user.id, PermissionType.MANAGE, session)


@router.post("", response_model=APIVersionResponse, status_code=status.HTTP_201_CREATED)
async def create_version(mock_api_id: UUID, data: APIVersionCreate,
                         current_user: User = Depends(get_current_user),
                         session: AsyncSession = Depends(get_database_session)):
    await _ensure_manage_access(mock_api_id, current_user, session)
    version = await APIVersionService(session).create_version(mock_api_id, data)
    await session.commit()
    return version


@router.get("", response_model=APIVersionListResponse)
async def list_versions(mock_api_id: UUID, page: int = Query(1, ge=1),
                        page_size: int = Query(20, ge=1, le=100),
                        is_active: bool | None = Query(None),
                        current_user: User = Depends(get_current_user),
                        session: AsyncSession = Depends(get_database_session)):
    await _get_api(mock_api_id, current_user, session)
    items, total, total_pages = await APIVersionService(session).list_versions(
        mock_api_id, page=page, page_size=page_size, is_active=is_active
    )
    return APIVersionListResponse(items=items, page=page, page_size=page_size, total=total, total_pages=total_pages)


@router.get("/{version_id}", response_model=APIVersionResponse)
async def get_version(mock_api_id: UUID, version_id: UUID,
                      current_user: User = Depends(get_current_user),
                      session: AsyncSession = Depends(get_database_session)):
    await _get_api(mock_api_id, current_user, session)
    return await APIVersionService(session).get_version(version_id, mock_api_id)


@router.patch("/{version_id}", response_model=APIVersionResponse)
async def update_version(mock_api_id: UUID, version_id: UUID, data: APIVersionUpdate,
                         current_user: User = Depends(get_current_user),
                         session: AsyncSession = Depends(get_database_session)):
    await _ensure_manage_access(mock_api_id, current_user, session)
    version = await APIVersionService(session).update_version(version_id, mock_api_id, data)
    await session.commit()
    await DynamicEndpointService(session, redis_client).invalidate(version_id)
    return version


@router.delete("/{version_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_version(mock_api_id: UUID, version_id: UUID,
                         current_user: User = Depends(get_current_user),
                         session: AsyncSession = Depends(get_database_session)):
    await _ensure_manage_access(mock_api_id, current_user, session)
    await APIVersionService(session).delete_version(version_id, mock_api_id)
    await session.commit()
    await DynamicEndpointService(session, redis_client).invalidate(version_id)
