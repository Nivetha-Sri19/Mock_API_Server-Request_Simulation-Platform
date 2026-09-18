from uuid import UUID

from sqlalchemy import String, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api_version import APIVersion
from app.repositories.base import BaseRepository


class APIVersionRepository(BaseRepository[APIVersion]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(
            session=session,
            model=APIVersion,
        )

    @staticmethod
    def _normalize_uuid(value: UUID | str) -> str:
        return str(value).replace("-", "").lower()

    @staticmethod
    def _uuid_column(column):
        return func.replace(
            cast(column, String),
            "-",
            "",
        )

    async def get_by_id_and_api(
        self,
        version_id: UUID,
        mock_api_id: UUID,
    ) -> APIVersion | None:
        statement = select(APIVersion).where(
            self._uuid_column(APIVersion.id)
            == self._normalize_uuid(version_id),
            self._uuid_column(APIVersion.mock_api_id)
            == self._normalize_uuid(mock_api_id),
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_version(
        self,
        mock_api_id: UUID,
        version: str,
    ) -> APIVersion | None:
        statement = select(APIVersion).where(
            self._uuid_column(APIVersion.mock_api_id)
            == self._normalize_uuid(mock_api_id),
            APIVersion.version == version,
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_active_version(
        self,
        mock_api_id: UUID,
    ) -> APIVersion | None:
        statement = (
            select(APIVersion)
            .where(
                self._uuid_column(APIVersion.mock_api_id)
                == self._normalize_uuid(mock_api_id),
                APIVersion.is_active.is_(True),
            )
            .order_by(APIVersion.created_at.desc())
        )

        result = await self.session.execute(statement)

        return result.scalars().first()

    async def list_by_api(
        self,
        mock_api_id: UUID,
        *,
        offset: int = 0,
        limit: int = 20,
        is_active: bool | None = None,
    ) -> tuple[list[APIVersion], int]:

        normalized_mock_api_id = self._normalize_uuid(mock_api_id)

        conditions = [
            self._uuid_column(APIVersion.mock_api_id)
            == normalized_mock_api_id
        ]

        if is_active is not None:
            conditions.append(
                APIVersion.is_active == is_active
            )

        query = (
            select(APIVersion)
            .where(*conditions)
            .order_by(APIVersion.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(query)

        items = list(result.scalars().all())

        count_query = (
            select(APIVersion)
            .where(*conditions)
        )

        total = await self.count(count_query)

        return items, total