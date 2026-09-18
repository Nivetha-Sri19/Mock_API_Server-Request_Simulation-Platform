from math import ceil
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.messages import USER_ALREADY_EXISTS, USER_NOT_FOUND
from app.core.exceptions import ConflictException, NotFoundException
from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.repository = UserRepository(session)

    async def create_user(
        self,
        data: UserCreate,
    ) -> User:
        existing_user = await self.repository.get_by_email(
            data.email,
        )

        if existing_user:
            raise ConflictException(
                message=USER_ALREADY_EXISTS,
                error_code="USER_ALREADY_EXISTS",
            )

        user = User(
            email=data.email.lower().strip(),
            password_hash=hash_password(data.password),
            full_name=data.full_name.strip(),
        )

        return await self.repository.create(user)

    async def get_user(
        self,
        user_id: UUID,
    ) -> User:
        user = await self.repository.get_by_id(user_id)

        if user is None:
            raise NotFoundException(
                message=USER_NOT_FOUND,
                error_code="USER_NOT_FOUND",
            )

        return user

    async def get_active_user(
        self,
        user_id: UUID,
    ) -> User:
        user = await self.repository.get_active_by_id(user_id)

        if user is None:
            raise NotFoundException(
                message=USER_NOT_FOUND,
                error_code="USER_NOT_FOUND",
            )

        return user

    async def update_user(
        self,
        user_id: UUID,
        data: UserUpdate,
    ) -> User:
        user = await self.get_user(user_id)

        update_data = data.model_dump(
            exclude_unset=True,
        )

        if "full_name" in update_data:
            update_data["full_name"] = (
                update_data["full_name"].strip()
            )

        for field, value in update_data.items():
            setattr(user, field, value)

        await self.repository.session.flush()
        await self.repository.session.refresh(user)

        return user

    async def delete_user(
        self,
        user_id: UUID,
    ) -> None:
        user = await self.get_user(user_id)

        await self.repository.delete(user)

    async def list_users(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        is_active: bool | None = None,
    ) -> tuple[list[User], int, int]:
        offset = (page - 1) * page_size

        users, total = await self.repository.list_users(
            offset=offset,
            limit=page_size,
            is_active=is_active,
        )

        total_pages = ceil(total / page_size) if total else 0

        return users, total, total_pages