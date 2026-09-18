from datetime import datetime
from uuid import UUID

from pydantic import EmailStr, Field

from app.constants.enums import UserRole
from app.schemas.common import BaseSchema


class UserCreate(BaseSchema):
    email: EmailStr
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=150,
    )


class UserUpdate(BaseSchema):
    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )
    is_active: bool | None = None


class UserResponse(BaseSchema):
    id: UUID
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserListResponse(BaseSchema):
    items: list[UserResponse]
    page: int
    page_size: int
    total: int
    total_pages: int