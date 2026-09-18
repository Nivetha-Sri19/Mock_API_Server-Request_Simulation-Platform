from datetime import datetime
from uuid import UUID

from pydantic import Field, field_validator

from app.constants.enums import ResponseScenario
from app.schemas.common import BaseSchema


class ResponseTemplateCreate(BaseSchema):
    scenario: ResponseScenario
    status_code: int = Field(
        ...,
        ge=100,
        le=599,
    )
    headers: dict[str, str] = Field(
        default_factory=dict,
    )
    body: object | None = None
    delay_ms: int = Field(
        default=0,
        ge=0,
        le=300000,
    )

    @field_validator("headers")
    @classmethod
    def validate_headers(
        cls,
        value: dict[str, str],
    ) -> dict[str, str]:
        for key, header_value in value.items():
            if not key.strip():
                raise ValueError("Header name cannot be empty")

            if not isinstance(header_value, str):
                raise ValueError(
                    f"Header value for '{key}' must be a string"
                )

        return value


class ResponseTemplateUpdate(BaseSchema):
    status_code: int | None = Field(
        default=None,
        ge=100,
        le=599,
    )
    headers: dict[str, str] | None = None
    body: object | None = None
    delay_ms: int | None = Field(
        default=None,
        ge=0,
        le=300000,
    )


class ResponseTemplateResponse(BaseSchema):
    id: UUID
    api_version_id: UUID
    scenario: ResponseScenario
    status_code: int
    headers: dict[str, str] | None
    body: object | None
    delay_ms: int
    created_at: datetime
    updated_at: datetime


class ResponseTemplateListResponse(BaseSchema):
    items: list[ResponseTemplateResponse]
    page: int
    page_size: int
    total: int
    total_pages: int