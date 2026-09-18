from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.constants.enums import PermissionType
from app.schemas.common import BaseSchema


class APIPermissionCreate(BaseSchema):
    user_id: UUID
    permission: PermissionType


class APIPermissionUpdate(BaseSchema):
    permission: PermissionType


class APIPermissionResponse(BaseSchema):
    id: UUID
    mock_api_id: UUID
    user_id: UUID
    permission: PermissionType
    created_at: datetime
    updated_at: datetime


class APIPermissionListResponse(BaseSchema):
    items: list[APIPermissionResponse]
    page: int
    page_size: int
    total: int
    total_pages: int