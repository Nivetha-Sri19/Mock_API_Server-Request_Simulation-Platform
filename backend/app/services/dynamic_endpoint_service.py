from typing import Any
from uuid import UUID

from redis.asyncio import Redis
from sqlalchemy import String, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.api_version import APIVersion
from app.models.mock_api import MockAPI
from app.services.cache_service import CacheService


class DynamicEndpointService:
    CACHE_PREFIX = "mock_api:definition"

    def __init__(
        self,
        session: AsyncSession,
        redis_client: Redis,
    ) -> None:
        self.session = session
        self.cache = CacheService(redis_client)

    def _cache_key(
        self,
        api_version_id: UUID,
    ) -> str:
        return (
            f"{self.CACHE_PREFIX}:"
            f"{str(api_version_id)}"
        )

    @staticmethod
    def _normalize_uuid(
        value: UUID | str,
    ) -> str:
        return str(value).replace("-", "")

    async def get_definition(
        self,
        api_version_id: UUID,
    ) -> dict[str, Any] | None:

        normalized_id = self._normalize_uuid(
            api_version_id
        )

        statement = (
            select(APIVersion)
            .options(
                selectinload(
                    APIVersion.mock_api
                ),
                selectinload(
                    APIVersion.request_schema
                ),
                selectinload(
                    APIVersion.response_templates
                ),
            )
            .where(
                func.replace(
                    cast(
                        APIVersion.id,
                        String,
                    ),
                    "-",
                    "",
                )
                == normalized_id
            )
        )

        result = await self.session.execute(
            statement
        )

        api_version = result.scalar_one_or_none()

        if api_version is None:
            return None

        if not api_version.is_active:
            return None

        mock_api = api_version.mock_api

        if mock_api is None:
            return None

        if not mock_api.is_active:
            return None

        definition = self._serialize_definition(
            api_version=api_version,
            mock_api=mock_api,
        )

        # Keep Redis synchronized with the
        # database source of truth.
        await self.cache.set(
            self._cache_key(api_version_id),
            definition,
        )

        return definition

    async def find_matching_definitions(
        self,
        method: str,
    ) -> list[dict[str, Any]]:

        statement = (
            select(APIVersion)
            .options(
                selectinload(
                    APIVersion.mock_api
                ),
                selectinload(
                    APIVersion.request_schema
                ),
                selectinload(
                    APIVersion.response_templates
                ),
            )
            .where(
                APIVersion.is_active.is_(True)
            )
            .order_by(
                APIVersion.created_at.desc()
            )
        )

        result = await self.session.execute(
            statement
        )

        definitions: list[dict[str, Any]] = []

        for api_version in result.scalars().all():

            mock_api = api_version.mock_api

            if mock_api is None:
                continue

            if not mock_api.is_active:
                continue

            if not self._method_matches(
                mock_api.http_method.value,
                method,
            ):
                continue

            definitions.append(
                self._serialize_definition(
                    api_version=api_version,
                    mock_api=mock_api,
                )
            )

        return definitions

    async def invalidate(
        self,
        api_version_id: UUID,
    ) -> None:

        await self.cache.delete(
            self._cache_key(
                api_version_id
            )
        )

    async def invalidate_api(
        self,
        mock_api_id: UUID,
    ) -> None:

        normalized_id = self._normalize_uuid(
            mock_api_id
        )

        statement = select(
            APIVersion.id
        ).where(
            func.replace(
                cast(
                    APIVersion.mock_api_id,
                    String,
                ),
                "-",
                "",
            )
            == normalized_id
        )

        result = await self.session.execute(
            statement
        )

        version_ids = list(
            result.scalars().all()
        )

        for version_id in version_ids:
            await self.invalidate(
                version_id
            )

    @staticmethod
    def _method_matches(
        configured_method: str,
        method: str,
    ) -> bool:

        return (
            configured_method.upper()
            == method.upper()
        )

    @staticmethod
    def _serialize_definition(
        *,
        api_version: APIVersion,
        mock_api: MockAPI,
    ) -> dict[str, Any]:

        request_schema = (
            api_version.request_schema
        )

        return {
            "api_id": str(
                mock_api.id
            ),

            "api_version_id": str(
                api_version.id
            ),

            "owner_id": str(
                mock_api.user_id
            ),

            "name": mock_api.name,

            "base_path": mock_api.base_path,

            "http_method":
                mock_api.http_method.value,

            "version":
                api_version.version,

            "is_private":
                mock_api.is_private,

            "is_active": (
                mock_api.is_active
                and api_version.is_active
            ),

            "request_schema": {
                "query_parameters": (
                    request_schema.query_parameters
                    if request_schema
                    else []
                ),

                "path_parameters": (
                    request_schema.path_parameters
                    if request_schema
                    else []
                ),

                "headers": (
                    request_schema.headers
                    if request_schema
                    else []
                ),

                "body_schema": (
                    request_schema.body_schema
                    if request_schema
                    else None
                ),
            },

            "responses": [
                {
                    "id": str(
                        template.id
                    ),

                    "scenario":
                        template.scenario,

                    "status_code":
                        template.status_code,

                    "headers":
                        template.headers or {},

                    "body":
                        template.body,

                    "delay_ms":
                        template.delay_ms,
                }
                for template
                in api_version.response_templates
            ],
        }