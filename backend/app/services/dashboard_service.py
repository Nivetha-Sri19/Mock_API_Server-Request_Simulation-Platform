from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mock_api import MockAPI
from app.schemas.dashboard import (
    DashboardResponse,
    DashboardSummary,
    MostUsedEndpoint,
)
from app.services.request_log_service import RequestLogService


class DashboardService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.request_log_service = RequestLogService(session)

    async def get_dashboard(
        self,
        user_id: UUID,
    ) -> DashboardResponse:
        total_mock_apis = await self._count_mock_apis(
            user_id=user_id,
        )

        active_mock_apis = await self._count_mock_apis(
            user_id=user_id,
            is_active=True,
        )

        total_requests = (
            await self.request_log_service.get_request_count(
                user_id=user_id,
            )
        )

        error_requests = (
            await self.request_log_service.get_error_count(
                user_id=user_id,
            )
        )

        average_response_time = (
            await self.request_log_service.get_average_response_time(
                user_id=user_id,
            )
        )

        most_used_data = (
            await self.request_log_service.get_most_used_endpoints(
                user_id=user_id,
            )
        )

        most_used_endpoints = [
            MostUsedEndpoint.model_validate(item)
            for item in most_used_data
        ]

        return DashboardResponse(
            summary=DashboardSummary(
                total_mock_apis=total_mock_apis,
                active_mock_apis=active_mock_apis,
                total_requests=total_requests,
                error_requests=error_requests,
                average_response_time_ms=round(
                    average_response_time,
                    2,
                ),
            ),
            most_used_endpoints=most_used_endpoints,
            generated_at=datetime.now(timezone.utc),
        )

    async def _count_mock_apis(
        self,
        *,
        user_id: UUID,
        is_active: bool | None = None,
    ) -> int:
        statement = select(
            func.count(MockAPI.id)
        ).where(
            MockAPI.user_id == user_id,
        )

        if is_active is not None:
            statement = statement.where(
                MockAPI.is_active == is_active,
            )

        result = await self.session.execute(statement)

        return int(result.scalar_one())