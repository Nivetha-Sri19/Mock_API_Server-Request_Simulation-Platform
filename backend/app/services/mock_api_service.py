from math import ceil
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.messages import (
    MOCK_API_ALREADY_EXISTS,
    MOCK_API_NOT_FOUND,
)
from app.core.exceptions import (
    ConflictException,
    NotFoundException,
)
from app.models.mock_api import MockAPI
from app.repositories.mock_api_repository import (
    MockAPIRepository,
)
from app.schemas.mock_api import (
    MockAPICreate,
    MockAPIUpdate,
)


class MockAPIService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.repository = MockAPIRepository(
            session
        )

    async def create_api(
        self,
        user_id: UUID,
        data: MockAPICreate,
    ) -> MockAPI:

        existing_api = (
            await self.repository
            .get_by_path_and_method_and_owner(
                base_path=data.base_path,
                http_method=data.http_method,
                user_id=user_id,
            )
        )

        if existing_api:
            raise ConflictException(
                message=MOCK_API_ALREADY_EXISTS,
                error_code="MOCK_API_ALREADY_EXISTS",
            )

        mock_api = MockAPI(
            user_id=user_id,
            name=data.name.strip(),
            description=data.description,
            base_path=data.base_path,
            http_method=data.http_method,
            is_private=data.is_private,
            is_active=True,
        )

        return await self.repository.create(
            mock_api
        )

    async def get_api(
        self,
        api_id: UUID,
        user_id: UUID,
    ) -> MockAPI:

        mock_api = (
            await self.repository
            .get_by_id_and_owner(
                api_id=api_id,
                user_id=user_id,
            )
        )

        if mock_api is None:
            raise NotFoundException(
                message=MOCK_API_NOT_FOUND,
                error_code="MOCK_API_NOT_FOUND",
            )

        return mock_api

    async def update_api(
        self,
        api_id: UUID,
        user_id: UUID,
        data: MockAPIUpdate,
    ) -> MockAPI:

        mock_api = await self.get_api(
            api_id=api_id,
            user_id=user_id,
        )

        update_data = data.model_dump(
            exclude_unset=True
        )

        if (
            "name" in update_data
            and update_data["name"]
        ):
            update_data["name"] = (
                update_data["name"].strip()
            )

        new_path = update_data.get(
            "base_path",
            mock_api.base_path,
        )

        new_method = update_data.get(
            "http_method",
            mock_api.http_method,
        )

        if (
            new_path
            != mock_api.base_path
            or new_method
            != mock_api.http_method
        ):
            existing_api = (
                await self.repository
                .get_by_path_and_method_and_owner(
                    base_path=new_path,
                    http_method=new_method,
                    user_id=user_id,
                )
            )

            if (
                existing_api
                and existing_api.id
                != mock_api.id
            ):
                raise ConflictException(
                    message=MOCK_API_ALREADY_EXISTS,
                    error_code="MOCK_API_ALREADY_EXISTS",
                )

        for field, value in update_data.items():
            setattr(
                mock_api,
                field,
                value,
            )

        await self.repository.session.flush()

        await self.repository.session.refresh(
            mock_api
        )

        return mock_api

    async def delete_api(
        self,
        api_id: UUID,
        user_id: UUID,
    ) -> None:

        mock_api = await self.get_api(
            api_id=api_id,
            user_id=user_id,
        )

        await self.repository.delete(
            mock_api
        )

    async def activate_api(
        self,
        api_id: UUID,
        user_id: UUID,
    ) -> MockAPI:

        mock_api = await self.get_api(
            api_id=api_id,
            user_id=user_id,
        )

        mock_api.is_active = True

        await self.repository.session.flush()

        await self.repository.session.refresh(
            mock_api
        )

        return mock_api

    async def deactivate_api(
        self,
        api_id: UUID,
        user_id: UUID,
    ) -> MockAPI:

        mock_api = await self.get_api(
            api_id=api_id,
            user_id=user_id,
        )

        mock_api.is_active = False

        await self.repository.session.flush()

        await self.repository.session.refresh(
            mock_api
        )

        return mock_api

    async def list_apis(
        self,
        user_id: UUID,
        *,
        page: int = 1,
        page_size: int = 20,
        is_active: bool | None = None,
        is_private: bool | None = None,
        http_method=None,
    ) -> tuple[
        list[MockAPI],
        int,
        int,
    ]:

        page = max(1, page)
        page_size = max(
            1,
            min(page_size, 100),
        )

        normalized_method = (
            http_method.value
            if hasattr(
                http_method,
                "value",
            )
            else http_method
        )

        items, total = (
            await self.repository.list_by_owner(
                user_id=user_id,
                page=page,
                page_size=page_size,
                is_active=is_active,
                is_private=is_private,
                http_method=normalized_method,
            )
        )

        total_pages = (
            ceil(total / page_size)
            if total
            else 0
        )

        return (
            items,
            total,
            total_pages,
        )