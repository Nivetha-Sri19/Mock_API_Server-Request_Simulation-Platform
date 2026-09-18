from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.enums import PermissionType, UserRole
from app.constants.messages import PERMISSION_DENIED
from app.core.exceptions import AuthorizationException
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_database_session
from app.models.user import User
from app.services.permission_service import PermissionService


def require_api_permission(permission: PermissionType):
    async def permission_dependency(
        mock_api_id: UUID,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_database_session),
    ) -> User:
        if current_user.role == UserRole.ADMIN:
            return current_user

        permission_service = PermissionService(session)

        await permission_service.require_permission(
            mock_api_id=mock_api_id,
            user_id=current_user.id,
            permission=permission,
        )

        return current_user

    return permission_dependency


async def check_api_permission(
    mock_api_id: UUID,
    user_id: UUID,
    permission: PermissionType,
    session: AsyncSession,
) -> None:
    permission_service = PermissionService(session)

    allowed = await permission_service.has_permission(
        mock_api_id=mock_api_id,
        user_id=user_id,
        permission=permission,
    )

    if not allowed:
        raise AuthorizationException(
            message=PERMISSION_DENIED,
            error_code="PERMISSION_DENIED",
        )