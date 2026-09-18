from math import ceil
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.enums import PermissionType
from app.constants.messages import PERMISSION_DENIED, PERMISSION_NOT_FOUND
from app.core.exceptions import ConflictException, NotFoundException
from app.models.api_permission import APIPermission
from app.repositories.api_permission_repository import (
    APIPermissionRepository,
)
from app.schemas.api_permission import (
    APIPermissionCreate,
    APIPermissionUpdate,
)


class PermissionService:
    def __init__(self, session: AsyncSession) -> None:
        self.repository = APIPermissionRepository(session)

    async def create_permission(
        self,
        mock_api_id: UUID,
        data: APIPermissionCreate,
    ) -> APIPermission:
        existing = await self.repository.get_permission(
            mock_api_id=mock_api_id,
            user_id=data.user_id,
            permission=data.permission,
        )
        if existing:
            raise ConflictException(
                message="Permission already exists",
                error_code="PERMISSION_ALREADY_EXISTS",
            )
        permission = APIPermission(
            mock_api_id=mock_api_id,
            user_id=data.user_id,
            permission=data.permission.value,
        )

        return await self.repository.create(permission)

    async def get_permission(
        self,
        permission_id: UUID,
        mock_api_id: UUID,
    ) -> APIPermission:
        permission = await self.repository.get_by_id_and_api(
            permission_id=permission_id,
            mock_api_id=mock_api_id,
        )

        if permission is None:
            raise NotFoundException(
                message=PERMISSION_NOT_FOUND,
                error_code="PERMISSION_NOT_FOUND",
            )

        return permission

    async def update_permission(
        self,
        permission_id: UUID,
        mock_api_id: UUID,
        data: APIPermissionUpdate,
    ) -> APIPermission:
        permission = await self.get_permission(
            permission_id=permission_id,
            mock_api_id=mock_api_id,
        )

        permission.permission = data.permission.value

        await self.repository.session.flush()
        await self.repository.session.refresh(permission)

        return permission

    async def delete_permission(
        self,
        permission_id: UUID,
        mock_api_id: UUID,
    ) -> None:
        permission = await self.get_permission(
            permission_id=permission_id,
            mock_api_id=mock_api_id,
        )

        await self.repository.delete(permission)

    async def has_permission(
        self,
        mock_api_id: UUID,
        user_id: UUID,
        permission: PermissionType,
    ) -> bool:
        result = await self.repository.get_permission(
            mock_api_id=mock_api_id,
            user_id=user_id,
            permission=permission,
        )

        return result is not None

    async def require_permission(
        self,
        mock_api_id: UUID,
        user_id: UUID,
        permission: PermissionType,
    ) -> None:
        allowed = await self.has_permission(
            mock_api_id=mock_api_id,
            user_id=user_id,
            permission=permission,
        )

        if not allowed:
            from app.core.exceptions import AuthorizationException

            raise AuthorizationException(
                message=PERMISSION_DENIED,
                error_code="PERMISSION_DENIED",
            )

    async def list_permissions(
        self,
        mock_api_id: UUID,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[APIPermission], int, int]:
        offset = (page - 1) * page_size

        items, total = await self.repository.list_by_api(
            mock_api_id=mock_api_id,
            offset=offset,
            limit=page_size,
        )

        total_pages = ceil(total / page_size) if total else 0

        return items, total, total_pages