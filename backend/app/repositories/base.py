from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import Select, String, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base


ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    def __init__(
        self,
        session: AsyncSession,
        model: type[ModelT],
    ) -> None:
        self.session = session
        self.model = model

    async def create(self, instance: ModelT) -> ModelT:
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def get_by_id(
        self,
        object_id: UUID,
    ) -> ModelT | None:
        normalized_id = str(object_id)

        result = await self.session.execute(
            select(self.model).where(
                func.replace(
                    cast(self.model.id, String),
                    "-",
                    "",
                )
                == normalized_id.replace("-", "")
            )
        )

        return result.scalar_one_or_none()

    async def delete(
        self,
        instance: ModelT,
    ) -> None:
        await self.session.delete(instance)
        await self.session.flush()

    async def count(
        self,
        statement: Select,
    ) -> int:
        count_statement = select(
            func.count()
        ).select_from(
            statement
            .order_by(None)
            .limit(None)
            .offset(None)
            .subquery()
        )

        result = await self.session.execute(count_statement)

        return int(result.scalar_one())