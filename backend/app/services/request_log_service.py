from math import ceil
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.request_log import RequestLog
from app.repositories.request_log_repository import RequestLogRepository


class RequestLogService:
    def __init__(self, session: AsyncSession) -> None:
        self.repository = RequestLogRepository(session)

    async def create_log(
        self,
        *,
        api_version_id: UUID,
        endpoint: str,
        http_method: str,
        request_parameters: dict | None,
        request_headers: dict | None,
        request_body: object | None,
        response_status: int,
        response_time_ms: float,
        timestamp: datetime,
    ) -> RequestLog:
        log = RequestLog(
            api_version_id=api_version_id,
            endpoint=endpoint,
            http_method=http_method,
            request_parameters=request_parameters,
            request_headers=request_headers,
            request_body=request_body,
            response_status=response_status,
            response_time_ms=response_time_ms,
            timestamp=timestamp,
        )

        return await self.repository.create(log)

    async def list_logs(
        self,
        api_version_id: UUID,
        *,
        page: int = 1,
        page_size: int = 20,
        response_status: int | None = None,
        http_method: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> tuple[list[RequestLog], int, int]:
        offset = (page - 1) * page_size

        items, total = await self.repository.list_by_version(
            api_version_id=api_version_id,
            offset=offset,
            limit=page_size,
            response_status=response_status,
            http_method=http_method,
            start_time=start_time,
            end_time=end_time,
        )

        total_pages = ceil(total / page_size) if total else 0

        return items, total, total_pages

    async def get_request_count(
        self,
        user_id: UUID,
    ) -> int:
        return await self.repository.count_by_owner(user_id)

    async def get_error_count(
        self,
        user_id: UUID,
    ) -> int:
        return await self.repository.count_errors_by_owner(user_id)

    async def get_average_response_time(
        self,
        user_id: UUID,
    ) -> float:
        return await self.repository.get_average_response_time(user_id)

    async def get_most_used_endpoints(
        self,
        user_id: UUID,
        *,
        limit: int = 10,
    ) -> list[dict]:
        return await self.repository.get_most_used_endpoints(
            user_id=user_id,
            limit=limit,
        )