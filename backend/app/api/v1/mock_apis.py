from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.enums import HTTPMethod
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_database_session
from app.models.user import User
from app.schemas.mock_api import (
    MockAPICreate,
    MockAPIListResponse,
    MockAPIResponse,
    MockAPIUpdate,
)
from app.services.dynamic_endpoint_service import DynamicEndpointService
from app.services.mock_api_service import MockAPIService
from app.core.redis import redis_client


router = APIRouter(
    prefix="/mock-apis",
    tags=["Mock APIs"],
)


@router.post(
    "",
    response_model=MockAPIResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_mock_api(
    data: MockAPICreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_database_session),
) -> MockAPIResponse:
    service = MockAPIService(session)

    mock_api = await service.create_api(
        user_id=current_user.id,
        data=data,
    )

    await session.commit()

    return mock_api


@router.get(
    "",
    response_model=MockAPIListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_mock_apis(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_active: bool | None = Query(default=None),
    is_private: bool | None = Query(default=None),
    http_method: HTTPMethod | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_database_session),
) -> MockAPIListResponse:
    service = MockAPIService(session)

    items, total, total_pages = await service.list_apis(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        is_active=is_active,
        is_private=is_private,
        http_method=http_method,
    )

    return MockAPIListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )


@router.get(
    "/{mock_api_id}",
    response_model=MockAPIResponse,
    status_code=status.HTTP_200_OK,
)
async def get_mock_api(
    mock_api_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_database_session),
) -> MockAPIResponse:
    service = MockAPIService(session)

    return await service.get_api(
        api_id=mock_api_id,
        user_id=current_user.id,
    )


@router.patch(
    "/{mock_api_id}",
    response_model=MockAPIResponse,
    status_code=status.HTTP_200_OK,
)
async def update_mock_api(
    mock_api_id: UUID,
    data: MockAPIUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_database_session),
) -> MockAPIResponse:
    service = MockAPIService(session)

    mock_api = await service.update_api(
        api_id=mock_api_id,
        user_id=current_user.id,
        data=data,
    )

    await session.commit()

    dynamic_service = DynamicEndpointService(
        session=session,
        redis_client=redis_client,
    )

    await dynamic_service.invalidate_api(
        mock_api_id=mock_api_id,
    )

    return mock_api


@router.post(
    "/{mock_api_id}/activate",
    response_model=MockAPIResponse,
    status_code=status.HTTP_200_OK,
)
async def activate_mock_api(
    mock_api_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_database_session),
) -> MockAPIResponse:
    service = MockAPIService(session)

    mock_api = await service.activate_api(
        api_id=mock_api_id,
        user_id=current_user.id,
    )

    await session.commit()

    dynamic_service = DynamicEndpointService(
        session=session,
        redis_client=redis_client,
    )

    await dynamic_service.invalidate_api(
        mock_api_id=mock_api_id,
    )

    return mock_api


@router.post(
    "/{mock_api_id}/deactivate",
    response_model=MockAPIResponse,
    status_code=status.HTTP_200_OK,
)
async def deactivate_mock_api(
    mock_api_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_database_session),
) -> MockAPIResponse:
    service = MockAPIService(session)

    mock_api = await service.deactivate_api(
        api_id=mock_api_id,
        user_id=current_user.id,
    )

    await session.commit()

    dynamic_service = DynamicEndpointService(
        session=session,
        redis_client=redis_client,
    )

    await dynamic_service.invalidate_api(
        mock_api_id=mock_api_id,
    )

    return mock_api


@router.delete(
    "/{mock_api_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_mock_api(
    mock_api_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_database_session),
) -> None:
    service = MockAPIService(session)

    await service.delete_api(
        api_id=mock_api_id,
        user_id=current_user.id,
    )

    await session.commit()

    dynamic_service = DynamicEndpointService(
        session=session,
        redis_client=redis_client,
    )

    await dynamic_service.invalidate_api(
        mock_api_id=mock_api_id,
    )