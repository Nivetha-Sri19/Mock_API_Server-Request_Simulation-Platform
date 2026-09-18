from math import ceil
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.messages import RESPONSE_TEMPLATE_NOT_FOUND
from app.core.exceptions import ConflictException, NotFoundException
from app.models.response_template import ResponseTemplate
from app.repositories.response_template_repository import (
    ResponseTemplateRepository,
)
from app.schemas.response_template import (
    ResponseTemplateCreate,
    ResponseTemplateUpdate,
)


class ScenarioService:
    def __init__(self, session: AsyncSession) -> None:
        self.repository = ResponseTemplateRepository(session)

    async def create_scenario(
        self,
        api_version_id: UUID,
        data: ResponseTemplateCreate,
    ) -> ResponseTemplate:

        existing = await self.repository.get_by_scenario(
            api_version_id=api_version_id,
            scenario=data.scenario.value,
        )

        if existing:
            raise ConflictException(
                message="Response scenario already exists for this API version",
                error_code="RESPONSE_SCENARIO_ALREADY_EXISTS",
            )

        template = ResponseTemplate(
            api_version_id=api_version_id,
            scenario=data.scenario.value,
            status_code=data.status_code,
            headers=data.headers,
            body=data.body,
            delay_ms=data.delay_ms,
        )

        return await self.repository.create(template)

    async def get_scenario(
        self,
        template_id: UUID,
        api_version_id: UUID,
    ) -> ResponseTemplate:

        template = await self.repository.get_by_id_and_version(
            template_id=template_id,
            api_version_id=api_version_id,
        )

        if template is None:
            raise NotFoundException(
                message=RESPONSE_TEMPLATE_NOT_FOUND,
                error_code="RESPONSE_TEMPLATE_NOT_FOUND",
            )

        return template

    async def update_scenario(
        self,
        template_id: UUID,
        api_version_id: UUID,
        data: ResponseTemplateUpdate,
    ) -> ResponseTemplate:

        template = await self.get_scenario(
            template_id=template_id,
            api_version_id=api_version_id,
        )

        update_data = data.model_dump(
            exclude_unset=True,
        )

        for field, value in update_data.items():
            setattr(template, field, value)

        await self.repository.session.flush()
        await self.repository.session.refresh(template)

        return template

    async def delete_scenario(
        self,
        template_id: UUID,
        api_version_id: UUID,
    ) -> None:

        template = await self.get_scenario(
            template_id=template_id,
            api_version_id=api_version_id,
        )

        await self.repository.delete(template)

    async def get_scenario_by_type(
        self,
        api_version_id: UUID,
        scenario: str,
    ) -> ResponseTemplate | None:

        return await self.repository.get_by_scenario(
            api_version_id=api_version_id,
            scenario=scenario,
        )

    async def list_scenarios(
        self,
        api_version_id: UUID,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ResponseTemplate], int, int]:

        offset = (page - 1) * page_size

        items, total = await self.repository.list_by_version(
            api_version_id=api_version_id,
            offset=offset,
            limit=page_size,
        )

        total_pages = ceil(total / page_size) if total else 0

        return items, total, total_pages