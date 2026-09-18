from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.constants.enums import HTTPMethod
from app.schemas.common import BaseSchema


class RequestLogResponse(BaseSchema):
    id: UUID
    api_version_id: UUID
    endpoint: str
    http_method: HTTPMethod
    request_parameters: dict | None
    request_headers: dict | None
    request_body: object | None
    response_status: int = Field(..., ge=100, le=599)
    response_time_ms: float = Field(..., ge=0)
    timestamp: datetime


class RequestLogListResponse(BaseSchema):
    items: list[RequestLogResponse]
    page: int
    page_size: int
    total: int
    total_pages: int