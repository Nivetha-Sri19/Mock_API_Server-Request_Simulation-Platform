from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ConflictException, UnauthorizedException
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.utils.jwt import create_access_token
from app.utils.password import get_password_hash, verify_password


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(session)

    async def register(
        self,
        email: str,
        password: str,
        full_name: str,
    ) -> User:
        existing_user = await self.user_repository.get_by_email(email)

        if existing_user:
            raise ConflictException(
                detail="A user with this email already exists."
            )

        password_hash = get_password_hash(password)

        user = User(
            email=email.lower().strip(),
            password_hash=password_hash,
            full_name=full_name.strip(),
        )

        return await self.user_repository.create(user)

    async def login(
        self,
        email: str,
        password: str,
    ) -> dict:
        user = await self.user_repository.get_by_email(
            email.lower().strip()
        )

        if not user:
            raise UnauthorizedException(
                detail="Invalid email or password."
            )

        if not user.is_active:
            raise UnauthorizedException(
                detail="User account is inactive."
            )

        if not verify_password(password, user.password_hash):
            raise UnauthorizedException(
                detail="Invalid email or password."
            )

        access_token = self.create_token(user)

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": self.token_expiry_seconds(),
        }

    def create_token(self, user: User) -> str:
        return create_access_token(
            subject=str(user.id),
            expires_delta=timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            ),
            additional_claims={
                "role": user.role.value,
                "email": user.email,
            },
        )

    @staticmethod
    def token_expiry_seconds() -> int:
        return settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60