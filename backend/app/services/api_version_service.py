from math import ceil
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.messages import (
    API_VERSION_ALREADY_EXISTS,
    API_VERSION_NOT_FOUND,
)
from app.core.exceptions import ConflictException, NotFoundException
from app.models.api_version import APIVersion
from app.repositories.api_version_repository import APIVersionRepository
from app.schemas.api_version import (
    APIVersionCreate,
    APIVersionUpdate,
)


class APIVersionService:
    def __init__(self, session: AsyncSession) -> None:
        self.repository = APIVersionRepository(session)

    async def create_version(
        self,
        mock_api_id: UUID,
        data: APIVersionCreate,
    ) -> APIVersion:
        existing_version = await self.repository.get_by_version(
            mock_api_id=mock_api_id,
            version=data.version,
        )

        if existing_version:
            raise ConflictException(
                message=API_VERSION_ALREADY_EXISTS,
                error_code="API_VERSION_ALREADY_EXISTS",
            )

        version = APIVersion(
            mock_api_id=mock_api_id,
            version=data.version,
            is_active=data.is_active,
        )

        return await self.repository.create(version)

    async def get_version(
        self,
        version_id: UUID,
        mock_api_id: UUID,
    ) -> APIVersion:
        version = await self.repository.get_by_id_and_api(
            version_id=version_id,
            mock_api_id=mock_api_id,
        )

        if version is None:
            raise NotFoundException(
                message=API_VERSION_NOT_FOUND,
                error_code="API_VERSION_NOT_FOUND",
            )

        return version

    async def update_version(
        self,
        version_id: UUID,
        mock_api_id: UUID,
        data: APIVersionUpdate,
    ) -> APIVersion:
        version = await self.get_version(
            version_id=version_id,
            mock_api_id=mock_api_id,
        )

        update_data = data.model_dump(
            exclude_unset=True,
        )

        for field, value in update_data.items():
            setattr(version, field, value)

        await self.repository.session.flush()
        await self.repository.session.refresh(version)

        return version

    async def delete_version(
        self,
        version_id: UUID,
        mock_api_id: UUID,
    ) -> None:
        version = await self.get_version(
            version_id=version_id,
            mock_api_id=mock_api_id,
        )

        await self.repository.delete(version)

    async def list_versions(
        self,
        mock_api_id: UUID,
        *,
        page: int = 1,
        page_size: int = 20,
        is_active: bool | None = None,
    ) -> tuple[list[APIVersion], int, int]:
        offset = (page - 1) * page_size

        items, total = await self.repository.list_by_api(
            mock_api_id=mock_api_id,
            offset=offset,
            limit=page_size,
            is_active=is_active,
        )

        total_pages = ceil(total / page_size) if total else 0

        return items, total, total_pages