from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(
            session=session,
            model=User,
        )

    async def get_by_email(
        self,
        email: str,
    ) -> User | None:
        statement = select(User).where(
            User.email == email.lower().strip()
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_active_by_id(
        self,
        user_id: UUID,
    ) -> User | None:
        statement = select(User).where(
            User.id == user_id,
            User.is_active.is_(True),
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def list_users(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        is_active: bool | None = None,
    ) -> tuple[list[User], int]:
        statement = select(User)

        if is_active is not None:
            statement = statement.where(
                User.is_active == is_active
            )

        statement = (
            statement
            .order_by(User.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(statement)

        users = list(result.scalars().all())

        count_statement = select(User)

        if is_active is not None:
            count_statement = count_statement.where(
                User.is_active == is_active
            )

        total = await self.count(count_statement)

        return users, total