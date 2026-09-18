from datetime import datetime
from uuid import UUID

from pydantic import Field, field_validator

from app.schemas.common import BaseSchema


class ParameterDefinition(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)
    type: str = Field(default="string", min_length=1, max_length=50)
    required: bool = False
    description: str | None = Field(default=None, max_length=500)
    default: object | None = None
    example: object | None = None


class HeaderDefinition(ParameterDefinition):
    pass


class RequestSchemaCreate(BaseSchema):
    query_parameters: list[ParameterDefinition] = Field(
        default_factory=list
    )
    path_parameters: list[ParameterDefinition] = Field(
        default_factory=list
    )
    headers: list[HeaderDefinition] = Field(
        default_factory=list
    )
    body_schema: dict | None = None

    @field_validator("body_schema")
    @classmethod
    def validate_body_schema(
        cls,
        value: dict | None,
    ) -> dict | None:
        if value is not None and not isinstance(value, dict):
            raise ValueError("Body schema must be a JSON object")

        return value


class RequestSchemaUpdate(BaseSchema):
    query_parameters: list[ParameterDefinition] | None = None
    path_parameters: list[ParameterDefinition] | None = None
    headers: list[HeaderDefinition] | None = None
    body_schema: dict | None = None


class RequestSchemaResponse(BaseSchema):
    id: UUID
    api_version_id: UUID
    query_parameters: list[dict] | None
    path_parameters: list[dict] | None
    headers: list[dict] | None
    body_schema: dict | None
    created_at: datetime
    updated_at: datetime