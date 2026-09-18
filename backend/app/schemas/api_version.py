from datetime import datetime
from uuid import UUID

from pydantic import Field, field_validator

from app.schemas.common import BaseSchema


class APIVersionCreate(BaseSchema):
    version: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )
    is_active: bool = True

    @field_validator("version")
    @classmethod
    def validate_version(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Version cannot be empty")

        if not value.lower().startswith("v"):
            value = f"v{value}"

        return value


class APIVersionUpdate(BaseSchema):
    is_active: bool | None = None


class APIVersionResponse(BaseSchema):
    id: UUID
    mock_api_id: UUID
    version: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class APIVersionListResponse(BaseSchema):
    items: list[APIVersionResponse]
    page: int
    page_size: int
    total: int
    total_pages: int