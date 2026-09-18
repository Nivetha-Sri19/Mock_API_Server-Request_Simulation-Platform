from datetime import datetime
from uuid import UUID

from sqlalchemy import String, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api_version import APIVersion
from app.models.mock_api import MockAPI
from app.models.request_log import RequestLog
from app.repositories.base import BaseRepository


class RequestLogRepository(BaseRepository[RequestLog]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(
            session=session,
            model=RequestLog,
        )

    @staticmethod
    def _normalize_uuid(value: UUID | str) -> str:
        return str(value).replace("-", "")

    @staticmethod
    def _normalized_uuid_column(column):
        return func.replace(
            cast(column, String),
            "-",
            "",
        )

    async def list_by_version(
        self,
        api_version_id: UUID,
        *,
        offset: int = 0,
        limit: int = 20,
        response_status: int | None = None,
        http_method: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> tuple[list[RequestLog], int]:

        normalized_version_id = self._normalize_uuid(
            api_version_id
        )

        version_condition = (
            self._normalized_uuid_column(
                RequestLog.api_version_id
            )
            == normalized_version_id
        )

        statement = (
            select(RequestLog)
            .where(version_condition)
        )

        if response_status is not None:
            statement = statement.where(
                RequestLog.response_status == response_status
            )

        if http_method is not None:
            statement = statement.where(
                RequestLog.http_method == http_method
            )

        if start_time is not None:
            statement = statement.where(
                RequestLog.timestamp >= start_time
            )

        if end_time is not None:
            statement = statement.where(
                RequestLog.timestamp <= end_time
            )

        statement = (
            statement
            .order_by(RequestLog.timestamp.desc())
            .offset(offset)
            .limit(limit)
        )

        items_result = await self.session.execute(statement)

        items = list(
            items_result.scalars().all()
        )

        count_statement = (
            select(RequestLog)
            .where(version_condition)
        )

        if response_status is not None:
            count_statement = count_statement.where(
                RequestLog.response_status == response_status
            )

        if http_method is not None:
            count_statement = count_statement.where(
                RequestLog.http_method == http_method
            )

        if start_time is not None:
            count_statement = count_statement.where(
                RequestLog.timestamp >= start_time
            )

        if end_time is not None:
            count_statement = count_statement.where(
                RequestLog.timestamp <= end_time
            )

        total = await self.count(
            count_statement
        )

        return items, total

    async def count_by_owner(
        self,
        user_id: UUID,
    ) -> int:

        normalized_user_id = self._normalize_uuid(
            user_id
        )

        statement = (
            select(
                func.count(RequestLog.id)
            )
            .join(
                APIVersion,
                self._normalized_uuid_column(
                    RequestLog.api_version_id
                )
                == self._normalized_uuid_column(
                    APIVersion.id
                ),
            )
            .join(
                MockAPI,
                self._normalized_uuid_column(
                    APIVersion.mock_api_id
                )
                == self._normalized_uuid_column(
                    MockAPI.id
                ),
            )
            .where(
                self._normalized_uuid_column(
                    MockAPI.user_id
                )
                == normalized_user_id
            )
        )

        result = await self.session.execute(
            statement
        )

        return int(result.scalar_one())

    async def count_errors_by_owner(
        self,
        user_id: UUID,
    ) -> int:

        normalized_user_id = self._normalize_uuid(
            user_id
        )

        statement = (
            select(
                func.count(RequestLog.id)
            )
            .join(
                APIVersion,
                self._normalized_uuid_column(
                    RequestLog.api_version_id
                )
                == self._normalized_uuid_column(
                    APIVersion.id
                ),
            )
            .join(
                MockAPI,
                self._normalized_uuid_column(
                    APIVersion.mock_api_id
                )
                == self._normalized_uuid_column(
                    MockAPI.id
                ),
            )
            .where(
                self._normalized_uuid_column(
                    MockAPI.user_id
                )
                == normalized_user_id,
                RequestLog.response_status >= 400,
            )
        )

        result = await self.session.execute(
            statement
        )

        return int(result.scalar_one())

    async def get_average_response_time(
        self,
        user_id: UUID,
    ) -> float:

        normalized_user_id = self._normalize_uuid(
            user_id
        )

        statement = (
            select(
                func.coalesce(
                    func.avg(
                        RequestLog.response_time_ms
                    ),
                    0.0,
                )
            )
            .join(
                APIVersion,
                self._normalized_uuid_column(
                    RequestLog.api_version_id
                )
                == self._normalized_uuid_column(
                    APIVersion.id
                ),
            )
            .join(
                MockAPI,
                self._normalized_uuid_column(
                    APIVersion.mock_api_id
                )
                == self._normalized_uuid_column(
                    MockAPI.id
                ),
            )
            .where(
                self._normalized_uuid_column(
                    MockAPI.user_id
                )
                == normalized_user_id
            )
        )

        result = await self.session.execute(
            statement
        )

        return float(
            result.scalar_one()
        )

    async def get_most_used_endpoints(
        self,
        user_id: UUID,
        *,
        limit: int = 10,
    ) -> list[dict]:

        normalized_user_id = self._normalize_uuid(
            user_id
        )

        statement = (
            select(
                RequestLog.api_version_id,
                RequestLog.endpoint,
                RequestLog.http_method,
                func.count(
                    RequestLog.id
                ).label(
                    "request_count"
                ),
            )
            .join(
                APIVersion,
                self._normalized_uuid_column(
                    RequestLog.api_version_id
                )
                == self._normalized_uuid_column(
                    APIVersion.id
                ),
            )
            .join(
                MockAPI,
                self._normalized_uuid_column(
                    APIVersion.mock_api_id
                )
                == self._normalized_uuid_column(
                    MockAPI.id
                ),
            )
            .where(
                self._normalized_uuid_column(
                    MockAPI.user_id
                )
                == normalized_user_id
            )
            .group_by(
                RequestLog.api_version_id,
                RequestLog.endpoint,
                RequestLog.http_method,
            )
            .order_by(
                func.count(
                    RequestLog.id
                ).desc()
            )
            .limit(limit)
        )

        result = await self.session.execute(
            statement
        )

        rows = result.mappings().all()

        return [
            dict(row)
            for row in rows
        ]