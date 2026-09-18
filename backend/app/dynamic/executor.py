from datetime import datetime, timezone
from time import perf_counter
from typing import Any
from uuid import UUID

import logging

from fastapi import Request
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.dynamic.response_builder import ResponseBuilder
from app.dynamic.scenario_handler import ScenarioHandler
from app.dynamic.validator import RequestValidator
from app.services.request_log_service import RequestLogService


logger = logging.getLogger(__name__)


class DynamicEndpointExecutor:

    def __init__(self) -> None:
        self.validator = RequestValidator()
        self.scenario_handler = ScenarioHandler()

    async def execute(
        self,
        *,
        request: Request,
        definition: dict[str, Any],
        path_parameters: dict[str, str],
        scenario: str | None = None,
        session: AsyncSession | None = None,
    ) -> Response:

        started = perf_counter()

        request_schema = definition.get(
            "request_schema"
        ) or {}

        query_parameters = {
            key: value
            for key, value in request.query_params.multi_items()
        }

        headers = {
            key: value
            for key, value in request.headers.items()
        }

        body: Any = None

        if request.method.upper() not in {
            "GET",
            "HEAD",
            "OPTIONS",
        }:
            body = await self._read_request_body(request)

        # Validate incoming request.
        await self.validator.validate(
            request_schema=request_schema,
            query_parameters=query_parameters,
            path_parameters=path_parameters,
            headers=headers,
            body=body,
        )

        # Select configured response scenario.
        template = self.scenario_handler.select_template(
            responses=definition.get("responses", []),
            scenario=scenario,
        )

        # Apply configured delay.
        await self.scenario_handler.apply_delay(
            template=template,
        )

        # Build response.
        response = ResponseBuilder.build(
            template=template,
        )

        response_time_ms = (
            perf_counter() - started
        ) * 1000

        # Create request history log.
        if session is not None:

            try:
                logged_body = body

                if isinstance(
                    logged_body,
                    bytes,
                ):
                    logged_body = logged_body.decode(
                        "utf-8",
                        errors="replace",
                    )

                api_version_id = UUID(
                    str(
                        definition[
                            "api_version_id"
                        ]
                    )
                )

                logger.info(
                    "Creating request log: "
                    "api_version_id=%s endpoint=%s "
                    "method=%s status=%s",
                    api_version_id,
                    request.url.path,
                    request.method.upper(),
                    response.status_code,
                )

                log_service = RequestLogService(
                    session
                )

                await log_service.create_log(
                    api_version_id=api_version_id,
                    endpoint=request.url.path,
                    http_method=request.method.upper(),
                    request_parameters=query_parameters,
                    request_headers=headers,
                    request_body=logged_body,
                    response_status=response.status_code,
                    response_time_ms=response_time_ms,
                    timestamp=datetime.now(
                        timezone.utc
                    ),
                )

                await session.commit()

                logger.info(
                    "Request log created successfully: "
                    "api_version_id=%s endpoint=%s",
                    api_version_id,
                    request.url.path,
                )

            except Exception:
                await session.rollback()

                logger.exception(
                    "Failed to create request log: "
                    "endpoint=%s method=%s",
                    request.url.path,
                    request.method.upper(),
                )

        return response

    @staticmethod
    async def _read_request_body(
        request: Request,
    ) -> Any:

        content_type = request.headers.get(
            "content-type",
            "",
        ).lower()

        if "application/json" in content_type:

            try:
                return await request.json()

            except ValueError:
                return None

        body = await request.body()

        if not body:
            return None

        try:
            return body.decode(
                "utf-8"
            )

        except UnicodeDecodeError:
            return body