from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.enums import PermissionType, UserRole
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_database_session
from app.dependencies.permissions import check_api_permission
from app.models.user import User
from app.repositories.mock_api_repository import MockAPIRepository
from app.schemas.request_schema import RequestSchemaCreate, RequestSchemaResponse, RequestSchemaUpdate
from app.services.dynamic_endpoint_service import DynamicEndpointService
from app.services.request_schema_service import RequestSchemaService
from app.core.redis import redis_client
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/mock-apis/{mock_api_id}/versions/{version_id}/request-schema", tags=["Request Schemas"])


async def _check(mock_api_id: UUID, user: User, session: AsyncSession, manage: bool = False):
    api = await MockAPIRepository(session).get_by_id(mock_api_id)
    if api is None:
        raise NotFoundException(message="Mock API not found", error_code="MOCK_API_NOT_FOUND")
    if user.role == UserRole.ADMIN or api.user_id == user.id:
        return
    await check_api_permission(mock_api_id, user.id, PermissionType.MANAGE if manage else PermissionType.VIEW, session)


@router.post("", response_model=RequestSchemaResponse, status_code=status.HTTP_201_CREATED)
async def create_schema(mock_api_id: UUID, version_id: UUID, data: RequestSchemaCreate,
                        current_user: User = Depends(get_current_user),
                        session: AsyncSession = Depends(get_database_session)):
    await _check(mock_api_id, current_user, session, True)
    schema = await RequestSchemaService(session).create_schema(version_id, data)
    await session.commit()
    return schema


@router.get("", response_model=RequestSchemaResponse)
async def get_schema(mock_api_id: UUID, version_id: UUID,
                     current_user: User = Depends(get_current_user),
                     session: AsyncSession = Depends(get_database_session)):
    await _check(mock_api_id, current_user, session)
    return await RequestSchemaService(session).get_schema(version_id)


@router.patch("", response_model=RequestSchemaResponse)
async def update_schema(mock_api_id: UUID, version_id: UUID, data: RequestSchemaUpdate,
                        current_user: User = Depends(get_current_user),
                        session: AsyncSession = Depends(get_database_session)):
    await _check(mock_api_id, current_user, session, True)
    schema = await RequestSchemaService(session).update_schema(version_id, data)
    await session.commit()
    await DynamicEndpointService(session, redis_client).invalidate(version_id)
    return schema


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schema(mock_api_id: UUID, version_id: UUID,
                        current_user: User = Depends(get_current_user),
                        session: AsyncSession = Depends(get_database_session)):
    await _check(mock_api_id, current_user, session, True)
    await RequestSchemaService(session).delete_schema(version_id)
    await session.commit()
    await DynamicEndpointService(session, redis_client).invalidate(version_id)
