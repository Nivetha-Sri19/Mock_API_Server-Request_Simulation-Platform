from uuid import UUID

from sqlalchemy import String, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.request_schema import RequestSchema
from app.repositories.base import BaseRepository


class RequestSchemaRepository(BaseRepository[RequestSchema]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session, model=RequestSchema)

    @staticmethod
    def _normalize_uuid(value: UUID | str) -> str:
        return str(value).replace("-", "")

    @staticmethod
    def _normalized_uuid_column(column):
        return func.replace(cast(column, String), "-", "")

    async def get_by_version(
        self,
        api_version_id: UUID,
    ) -> RequestSchema | None:
        normalized_version_id = self._normalize_uuid(api_version_id)

        statement = select(RequestSchema).where(
            self._normalized_uuid_column(
                RequestSchema.api_version_id
            ) == normalized_version_id
        )

        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_api_version(
        self,
        api_version_id: UUID,
    ) -> RequestSchema | None:
        return await self.get_by_version(api_version_id)

    async def get_by_id_and_version(
        self,
        schema_id: UUID,
        api_version_id: UUID,
    ) -> RequestSchema | None:
        normalized_schema_id = self._normalize_uuid(schema_id)
        normalized_version_id = self._normalize_uuid(api_version_id)

        statement = select(RequestSchema).where(
            self._normalized_uuid_column(
                RequestSchema.id
            ) == normalized_schema_id,
            self._normalized_uuid_column(
                RequestSchema.api_version_id
            ) == normalized_version_id,
        )

        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def delete_by_version(
        self,
        api_version_id: UUID,
    ) -> None:
        schema = await self.get_by_version(api_version_id)

        if schema is not None:
            await self.session.delete(schema)
            await self.session.flush()