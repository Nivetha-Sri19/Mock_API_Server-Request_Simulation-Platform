from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.models.request_schema import RequestSchema
from app.repositories.request_schema_repository import RequestSchemaRepository
from app.schemas.request_schema import RequestSchemaCreate, RequestSchemaUpdate


class RequestSchemaService:
    def __init__(self, session: AsyncSession) -> None:
        self.repository = RequestSchemaRepository(session)

    async def create_schema(self, api_version_id: UUID, data: RequestSchemaCreate) -> RequestSchema:
        existing = await self.repository.get_by_api_version(api_version_id)
        if existing:
            raise ConflictException(
                message="Request schema already exists for this API version",
                error_code="REQUEST_SCHEMA_ALREADY_EXISTS",
            )
        schema = RequestSchema(
            api_version_id=api_version_id,
            query_parameters=[item.model_dump() for item in data.query_parameters],
            path_parameters=[item.model_dump() for item in data.path_parameters],
            headers=[item.model_dump() for item in data.headers],
            body_schema=data.body_schema,
        )
        return await self.repository.create(schema)

    async def get_schema(self, api_version_id: UUID) -> RequestSchema:
        schema = await self.repository.get_by_api_version(api_version_id)
        if schema is None:
            raise NotFoundException(
                message="Request schema not found",
                error_code="REQUEST_SCHEMA_NOT_FOUND",
            )
        return schema

    async def update_schema(self, api_version_id: UUID, data: RequestSchemaUpdate) -> RequestSchema:
        schema = await self.get_schema(api_version_id)
        values = data.model_dump(exclude_unset=True)
        for field in ("query_parameters", "path_parameters", "headers"):
            if field in values and values[field] is not None:
                values[field] = [item.model_dump() if hasattr(item, "model_dump") else item for item in values[field]]
        for field, value in values.items():
            setattr(schema, field, value)
        await self.repository.session.flush()
        await self.repository.session.refresh(schema)
        return schema

    async def delete_schema(self, api_version_id: UUID) -> None:
        schema = await self.get_schema(api_version_id)
        await self.repository.delete(schema)
