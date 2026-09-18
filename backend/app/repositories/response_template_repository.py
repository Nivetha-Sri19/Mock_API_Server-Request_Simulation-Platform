from uuid import UUID

from sqlalchemy import String, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.enums import ResponseScenario
from app.models.response_template import ResponseTemplate
from app.repositories.base import BaseRepository


class ResponseTemplateRepository(BaseRepository[ResponseTemplate]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(
            session=session,
            model=ResponseTemplate,
        )

    @staticmethod
    def _normalize_uuid(value: UUID | str) -> str:
        return str(value).replace("-", "")

    @staticmethod
    def _normalized_column(column):
        return func.replace(
            cast(column, String),
            "-",
            "",
        )

    async def get_by_id_and_version(
        self,
        template_id: UUID,
        api_version_id: UUID,
    ) -> ResponseTemplate | None:

        normalized_template_id = self._normalize_uuid(template_id)
        normalized_version_id = self._normalize_uuid(api_version_id)

        statement = select(ResponseTemplate).where(
            self._normalized_column(ResponseTemplate.id)
            == normalized_template_id,
            self._normalized_column(ResponseTemplate.api_version_id)
            == normalized_version_id,
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_scenario(
        self,
        api_version_id: UUID,
        scenario: ResponseScenario | str,
    ) -> ResponseTemplate | None:

        normalized_version_id = self._normalize_uuid(api_version_id)

        scenario_value = (
            scenario.value
            if isinstance(scenario, ResponseScenario)
            else str(scenario)
        )

        statement = select(ResponseTemplate).where(
            self._normalized_column(ResponseTemplate.api_version_id)
            == normalized_version_id,
            ResponseTemplate.scenario == scenario_value,
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def list_by_version(
        self,
        api_version_id: UUID,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[ResponseTemplate], int]:

        normalized_version_id = self._normalize_uuid(api_version_id)

        version_condition = (
            self._normalized_column(ResponseTemplate.api_version_id)
            == normalized_version_id
        )

        statement = (
            select(ResponseTemplate)
            .where(version_condition)
            .order_by(ResponseTemplate.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(statement)

        items = list(result.scalars().all())

        count_statement = (
            select(ResponseTemplate)
            .where(version_condition)
        )

        total = await self.count(count_statement)

        return items, total