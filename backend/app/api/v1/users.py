from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthorizationException
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_database_session
from app.schemas.user import UserCreate, UserListResponse, UserResponse
from app.services.user_service import UserService


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


def _require_admin(current_user) -> None:
    if current_user.role.value != "admin":
        raise AuthorizationException(
            detail="Administrator access required",
            code="ADMIN_REQUIRED",
        )


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    payload: UserCreate,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_database_session),
):
    _require_admin(current_user)

    service = UserService(session)

    user = await service.create_user(
        data=payload,
    )

    await session.commit()

    return user


@router.get(
    "",
    response_model=UserListResponse,
)
async def list_users(
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    is_active: bool | None = Query(
        default=None,
    ),
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_database_session),
):
    _require_admin(current_user)

    service = UserService(session)

    users, total, total_pages = await service.list_users(
        page=page,
        page_size=page_size,
        is_active=is_active,
    )

    return UserListResponse(
        items=users,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
async def get_user(
    user_id: UUID,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_database_session),
):
    _require_admin(current_user)

    service = UserService(session)

    return await service.get_user(user_id)