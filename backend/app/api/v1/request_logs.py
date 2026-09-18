from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.enums import HTTPMethod, PermissionType, UserRole
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_database_session
from app.dependencies.permissions import check_api_permission
from app.models.user import User
from app.schemas.request_log import (
    RequestLogListResponse,
    RequestLogResponse,
)
from app.services.mock_api_service import MockAPIService
from app.services.request_log_service import RequestLogService


router = APIRouter(
    prefix="/mock-apis/{mock_api_id}/versions/{version_id}/logs",
    tags=["Request Logs"],
)


@router.get(
    "",
    response_model=RequestLogListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_request_logs(
    mock_api_id: UUID,
    version_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    response_status: int | None = Query(
        default=None,
        ge=100,
        le=599,
    ),
    http_method: HTTPMethod | None = Query(default=None),
    start_time: datetime | None = Query(default=None),
    end_time: datetime | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_database_session),
) -> RequestLogListResponse:
    mock_api_service = MockAPIService(session)

    mock_api = await mock_api_service.get_api(
        api_id=mock_api_id,
        user_id=current_user.id,
    )

    if (
        current_user.role != UserRole.ADMIN
        and mock_api.user_id != current_user.id
    ):
        await check_api_permission(
            mock_api_id=mock_api_id,
            user_id=current_user.id,
            permission=PermissionType.VIEW,
            session=session,
        )

    if (
        start_time is not None
        and end_time is not None
        and start_time > end_time
    ):
        from app.core.exceptions import BadRequestException

        raise BadRequestException(
            message="start_time cannot be later than end_time",
            error_code="INVALID_TIME_RANGE",
        )

    service = RequestLogService(session)

    items, total, total_pages = await service.list_logs(
        api_version_id=version_id,
        page=page,
        page_size=page_size,
        response_status=response_status,
        http_method=(
            http_method.value
            if http_method is not None
            else None
        ),
        start_time=start_time,
        end_time=end_time,
    )

    return RequestLogListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )