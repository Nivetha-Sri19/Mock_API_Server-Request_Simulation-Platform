from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DashboardSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_mock_apis: int = Field(..., ge=0)
    active_mock_apis: int = Field(..., ge=0)
    total_requests: int = Field(..., ge=0)
    error_requests: int = Field(..., ge=0)
    average_response_time_ms: float = Field(..., ge=0)


class MostUsedEndpoint(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    api_version_id: UUID
    endpoint: str
    http_method: str
    request_count: int = Field(..., ge=0)


class DashboardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    summary: DashboardSummary
    most_used_endpoints: list[MostUsedEndpoint]
    generated_at: datetime