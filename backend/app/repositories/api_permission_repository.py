from uuid import UUID

from sqlalchemy import String, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.enums import PermissionType
from app.models.api_permission import APIPermission
from app.repositories.base import BaseRepository


class APIPermissionRepository(BaseRepository[APIPermission]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(
            session=session,
            model=APIPermission,
        )

    @staticmethod
    def _normalize_uuid(value: UUID | str) -> str:
        return str(value).replace("-", "")

    @staticmethod
    def _normalized_uuid_column(column):
        return func.replace(
            cast(column, String),
            "-",
            "",
        )

    async def get_permission(
        self,
        mock_api_id: UUID,
        user_id: UUID,
        permission: PermissionType,
    ) -> APIPermission | None:

        normalized_mock_api_id = self._normalize_uuid(mock_api_id)
        normalized_user_id = self._normalize_uuid(user_id)

        permission_value = (
            permission.value
            if isinstance(permission, PermissionType)
            else str(permission)
        )

        statement = select(APIPermission).where(
            self._normalized_uuid_column(
                APIPermission.mock_api_id
            ) == normalized_mock_api_id,

            self._normalized_uuid_column(
                APIPermission.user_id
            ) == normalized_user_id,

            APIPermission.permission == permission_value,
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_id_and_api(
        self,
        permission_id: UUID,
        mock_api_id: UUID,
    ) -> APIPermission | None:

        normalized_permission_id = self._normalize_uuid(
            permission_id
        )

        normalized_mock_api_id = self._normalize_uuid(
            mock_api_id
        )

        statement = select(APIPermission).where(
            self._normalized_uuid_column(
                APIPermission.id
            ) == normalized_permission_id,

            self._normalized_uuid_column(
                APIPermission.mock_api_id
            ) == normalized_mock_api_id,
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def list_by_api(
        self,
        mock_api_id: UUID,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[APIPermission], int]:

        normalized_mock_api_id = self._normalize_uuid(
            mock_api_id
        )

        api_condition = (
            self._normalized_uuid_column(
                APIPermission.mock_api_id
            )
            == normalized_mock_api_id
        )

        statement = (
            select(APIPermission)
            .where(api_condition)
            .order_by(
                APIPermission.created_at.desc()
            )
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(statement)

        items = list(result.scalars().all())

        count_statement = (
            select(APIPermission)
            .where(api_condition)
        )

        total = await self.count(count_statement)

        return items, total