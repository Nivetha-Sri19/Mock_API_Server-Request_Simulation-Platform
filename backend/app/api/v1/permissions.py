from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.enums import PermissionType, UserRole
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_database_session
from app.models.user import User
from app.schemas.api_permission import (
    APIPermissionCreate,
    APIPermissionListResponse,
    APIPermissionResponse,
    APIPermissionUpdate,
)
from app.services.mock_api_service import MockAPIService
from app.services.permission_service import PermissionService


router = APIRouter(
    prefix="/mock-apis/{mock_api_id}/permissions",
    tags=["API Permissions"],
)


async def _ensure_manage_access(
    *,
    mock_api_id: UUID,
    current_user: User,
    session: AsyncSession,
) -> None:
    from app.core.exceptions import NotFoundException
    from app.repositories.mock_api_repository import MockAPIRepository

    mock_api = await MockAPIRepository(session).get_by_id(mock_api_id)
    if mock_api is None:
        raise NotFoundException(message="Mock API not found", error_code="MOCK_API_NOT_FOUND")

    if current_user.role == UserRole.ADMIN or mock_api.user_id == current_user.id:
        return

    await PermissionService(session).require_permission(
        mock_api_id=mock_api_id,
        user_id=current_user.id,
        permission=PermissionType.MANAGE,
    )

@router.post(
    "",
    response_model=APIPermissionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_permission(
    mock_api_id: UUID,
    data: APIPermissionCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_database_session),
) -> APIPermissionResponse:
    await _ensure_manage_access(
        mock_api_id=mock_api_id,
        current_user=current_user,
        session=session,
    )

    service = PermissionService(session)

    permission = await service.create_permission(
        mock_api_id=mock_api_id,
        data=data,
    )

    await session.commit()

    return permission


@router.get(
    "",
    response_model=APIPermissionListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_permissions(
    mock_api_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_database_session),
) -> APIPermissionListResponse:
    await _ensure_manage_access(
        mock_api_id=mock_api_id,
        current_user=current_user,
        session=session,
    )

    service = PermissionService(session)

    items, total, total_pages = await service.list_permissions(
        mock_api_id=mock_api_id,
        page=page,
        page_size=page_size,
    )

    return APIPermissionListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )


@router.get(
    "/{permission_id}",
    response_model=APIPermissionResponse,
    status_code=status.HTTP_200_OK,
)
async def get_permission(
    mock_api_id: UUID,
    permission_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_database_session),
) -> APIPermissionResponse:
    await _ensure_manage_access(
        mock_api_id=mock_api_id,
        current_user=current_user,
        session=session,
    )

    service = PermissionService(session)

    return await service.get_permission(
        permission_id=permission_id,
        mock_api_id=mock_api_id,
    )


@router.patch(
    "/{permission_id}",
    response_model=APIPermissionResponse,
    status_code=status.HTTP_200_OK,
)
async def update_permission(
    mock_api_id: UUID,
    permission_id: UUID,
    data: APIPermissionUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_database_session),
) -> APIPermissionResponse:
    await _ensure_manage_access(
        mock_api_id=mock_api_id,
        current_user=current_user,
        session=session,
    )

    service = PermissionService(session)

    permission = await service.update_permission(
        permission_id=permission_id,
        mock_api_id=mock_api_id,
        data=data,
    )

    await session.commit()

    return permission


@router.delete(
    "/{permission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_permission(
    mock_api_id: UUID,
    permission_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_database_session),
) -> None:
    await _ensure_manage_access(
        mock_api_id=mock_api_id,
        current_user=current_user,
        session=session,
    )

    service = PermissionService(session)

    await service.delete_permission(
        permission_id=permission_id,
        mock_api_id=mock_api_id,
    )

    await session.commit()