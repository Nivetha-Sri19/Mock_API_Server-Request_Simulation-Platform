import json
from typing import Any

from fastapi.responses import JSONResponse, Response

from app.constants.enums import ResponseScenario
from app.core.exceptions import ValidationException


class ResponseBuilder:
    @staticmethod
    def build(
        *,
        template: dict[str, Any],
    ) -> Response:
        status_code = int(template.get("status_code", 200))
        headers = ResponseBuilder._normalize_headers(
            template.get("headers"),
        )
        body = template.get("body")
        scenario = template.get("scenario")

        if status_code < 100 or status_code > 599:
            raise ValidationException(
                message="Invalid response status code",
                error_code="INVALID_RESPONSE_STATUS",
            )

        if status_code in {204, 304}:
            return Response(
                content=None,
                status_code=status_code,
                headers=headers,
            )

        if ResponseBuilder._is_json_body(body):
            return JSONResponse(
                content=body,
                status_code=status_code,
                headers=headers,
            )

        if body is None:
            return Response(
                content=None,
                status_code=status_code,
                headers=headers,
            )

        if isinstance(body, bytes):
            return Response(
                content=body,
                status_code=status_code,
                headers=headers,
            )

        if isinstance(body, str):
            content = body
        else:
            content = json.dumps(
                body,
                ensure_ascii=False,
                default=str,
            )

        if scenario == ResponseScenario.CUSTOM.value:
            return Response(
                content=content,
                status_code=status_code,
                headers=headers,
                media_type=headers.get(
                    "Content-Type",
                    "application/json",
                ),
            )

        return Response(
            content=content,
            status_code=status_code,
            headers=headers,
            media_type=headers.get(
                "Content-Type",
                "application/json",
            ),
        )

    @staticmethod
    def _normalize_headers(
        headers: Any,
    ) -> dict[str, str]:
        if not isinstance(headers, dict):
            return {}

        normalized: dict[str, str] = {}

        for key, value in headers.items():
            if key is None:
                continue

            header_name = str(key).strip()

            if not header_name:
                continue

            normalized[header_name] = str(value)

        return normalized

    @staticmethod
    def _is_json_body(body: Any) -> bool:
        return isinstance(
            body,
            (dict, list),
        )