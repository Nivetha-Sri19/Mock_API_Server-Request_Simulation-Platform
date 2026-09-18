from datetime import datetime
from uuid import UUID

from pydantic import Field, field_validator

from app.constants.enums import HTTPMethod
from app.schemas.common import BaseSchema


class MockAPIBase(BaseSchema):
    name: str = Field(..., min_length=2, max_length=150)
    description: str | None = Field(default=None, max_length=2000)
    base_path: str = Field(..., min_length=1, max_length=500)
    http_method: HTTPMethod
    is_private: bool = False

    @field_validator("base_path")
    @classmethod
    def validate_base_path(cls, value: str) -> str:
        value = value.strip()
        if not value.startswith("/"):
            value = f"/{value}"
        if value != "/" and value.endswith("/"):
            value = value.rstrip("/")
        if "//" in value:
            raise ValueError("Base path cannot contain consecutive slashes")
        return value


class MockAPICreate(MockAPIBase):
    pass


class MockAPIUpdate(BaseSchema):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    description: str | None = Field(default=None, max_length=2000)
    base_path: str | None = Field(default=None, min_length=1, max_length=500)
    http_method: HTTPMethod | None = None
    is_private: bool | None = None
    is_active: bool | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else None

    @field_validator("base_path")
    @classmethod
    def validate_base_path(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value.startswith("/"):
            value = f"/{value}"
        if value != "/" and value.endswith("/"):
            value = value.rstrip("/")
        if "//" in value:
            raise ValueError("Base path cannot contain consecutive slashes")
        return value


class MockAPIResponse(BaseSchema):
    id: UUID
    user_id: UUID
    name: str
    description: str | None
    base_path: str
    http_method: HTTPMethod
    is_active: bool
    is_private: bool
    created_at: datetime
    updated_at: datetime


class MockAPIListResponse(BaseSchema):
    items: list[MockAPIResponse]
    page: int
    page_size: int
    total: int
    total_pages: int


class MockAPIExecutionRequest(BaseSchema):
    method: HTTPMethod
    path: str
    query_parameters: dict[str, str] = Field(default_factory=dict)
    headers: dict[str, str] = Field(default_factory=dict)
    body: object | None = None
