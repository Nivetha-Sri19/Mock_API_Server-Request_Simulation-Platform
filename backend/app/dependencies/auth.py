from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationException
from app.dependencies.database import get_database_session
from app.repositories.user_repository import UserRepository
from app.utils.jwt import decode_access_token


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/token"
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_database_session),
):
    payload = decode_access_token(token)

    if not payload:
        raise AuthenticationException(
            detail="Invalid or expired access token."
        )

    subject = payload.get("sub")

    if not subject:
        raise AuthenticationException(
            detail="Invalid access token."
        )

    try:
        user_id = UUID(str(subject))
    except (ValueError, TypeError):
        raise AuthenticationException(
            detail="Invalid access token subject."
        )

    repository = UserRepository(session)

    user = await repository.get_by_id(user_id)

    if not user:
        raise AuthenticationException(
            detail="User not found."
        )

    if not user.is_active:
        raise AuthenticationException(
            detail="User account is inactive."
        )

    return user