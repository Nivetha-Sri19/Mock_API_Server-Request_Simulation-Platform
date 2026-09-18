from uuid import UUID

from sqlalchemy import String, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mock_api import MockAPI
from app.repositories.base import BaseRepository


class MockAPIRepository(BaseRepository[MockAPI]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, MockAPI)

    async def get_by_id_and_owner(
        self,
        api_id: UUID,
        user_id: UUID,
    ) -> MockAPI | None:
        normalized_api_id = str(api_id).replace("-", "")
        normalized_user_id = str(user_id).replace("-", "")

        result = await self.session.execute(
            select(MockAPI).where(
                func.replace(
                    cast(MockAPI.id, String),
                    "-",
                    "",
                )
                == normalized_api_id,
                func.replace(
                    cast(MockAPI.user_id, String),
                    "-",
                    "",
                )
                == normalized_user_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_by_path_and_method_and_owner(
        self,
        base_path: str,
        http_method: str,
        user_id: UUID,
    ) -> MockAPI | None:
        result = await self.session.execute(
            select(MockAPI).where(
                MockAPI.base_path == base_path.strip(),
                MockAPI.http_method == http_method,
                func.replace(
                    cast(MockAPI.user_id, String),
                    "-",
                    "",
                )
                == str(user_id).replace("-", ""),
            )
        )

        return result.scalar_one_or_none()

    async def get_active_by_path_and_method(
        self,
        base_path: str,
        http_method: str,
    ) -> MockAPI | None:
        result = await self.session.execute(
            select(MockAPI).where(
                MockAPI.base_path == base_path.strip(),
                MockAPI.http_method == http_method,
                MockAPI.is_active.is_(True),
            )
        )

        return result.scalar_one_or_none()

    async def list_by_owner(
        self,
        user_id: UUID,
        *,
        page: int = 1,
        page_size: int = 20,
        http_method: str | None = None,
        is_active: bool | None = None,
        is_private: bool | None = None,
    ) -> tuple[list[MockAPI], int]:

        page = max(1, page)
        page_size = max(1, min(page_size, 100))

        conditions = [
            func.replace(
                cast(MockAPI.user_id, String),
                "-",
                "",
            )
            == str(user_id).replace("-", "")
        ]

        if http_method is not None:
            conditions.append(
                MockAPI.http_method == http_method
            )

        if is_active is not None:
            conditions.append(
                MockAPI.is_active.is_(is_active)
            )

        if is_private is not None:
            conditions.append(
                MockAPI.is_private.is_(is_private)
            )

        count_query = (
            select(func.count())
            .select_from(MockAPI)
            .where(*conditions)
        )

        count_result = await self.session.execute(
            count_query
        )

        total = int(
            count_result.scalar_one()
        )

        offset = (page - 1) * page_size

        query = (
            select(MockAPI)
            .where(*conditions)
            .order_by(
                MockAPI.created_at.desc()
            )
            .offset(offset)
            .limit(page_size)
        )

        result = await self.session.execute(
            query
        )

        items = list(
            result.scalars().all()
        )

        return items, total

    async def exists_by_path_and_method_and_owner(
        self,
        base_path: str,
        http_method: str,
        user_id: UUID,
        *,
        exclude_id: UUID | None = None,
    ) -> bool:

        conditions = [
            MockAPI.base_path
            == base_path.strip(),
            MockAPI.http_method
            == http_method,
            func.replace(
                cast(MockAPI.user_id, String),
                "-",
                "",
            )
            == str(user_id).replace("-", ""),
        ]

        if exclude_id is not None:
            conditions.append(
                func.replace(
                    cast(MockAPI.id, String),
                    "-",
                    "",
                )
                != str(exclude_id).replace("-", "")
            )

        result = await self.session.execute(
            select(MockAPI.id)
            .where(*conditions)
            .limit(1)
        )

        return (
            result.scalar_one_or_none()
            is not None
        )

    async def activate(
        self,
        mock_api: MockAPI,
    ) -> MockAPI:
        mock_api.is_active = True

        await self.session.flush()
        await self.session.refresh(
            mock_api
        )

        return mock_api

    async def deactivate(
        self,
        mock_api: MockAPI,
    ) -> MockAPI:
        mock_api.is_active = False

        await self.session.flush()
        await self.session.refresh(
            mock_api
        )

        return mock_api