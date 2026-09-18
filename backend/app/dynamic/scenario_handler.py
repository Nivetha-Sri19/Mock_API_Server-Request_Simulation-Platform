import asyncio
from typing import Any

from app.constants.enums import ResponseScenario
from app.core.exceptions import NotFoundException


class ScenarioHandler:
    DEFAULT_SCENARIO = ResponseScenario.SUCCESS.value

    def select_template(
        self,
        *,
        responses: list[dict[str, Any]],
        scenario: str | None = None,
    ) -> dict[str, Any]:
        if not responses:
            raise NotFoundException(
                message="No response template configured",
                error_code="RESPONSE_TEMPLATE_NOT_FOUND",
            )

        requested_scenario = (
            scenario.strip().lower()
            if scenario
            else self.DEFAULT_SCENARIO
        )

        for response in responses:
            configured_scenario = str(
                response.get("scenario", ""),
            ).strip().lower()

            if configured_scenario == requested_scenario:
                return response

        if requested_scenario != self.DEFAULT_SCENARIO:
            for response in responses:
                if (
                    str(response.get("scenario", "")).strip().lower()
                    == self.DEFAULT_SCENARIO
                ):
                    return response

        raise NotFoundException(
            message=(
                f"Response scenario '{requested_scenario}' "
                "is not configured"
            ),
            error_code="RESPONSE_SCENARIO_NOT_FOUND",
        )

    async def apply_delay(
        self,
        *,
        template: dict[str, Any],
    ) -> None:
        delay_ms = template.get("delay_ms", 0)

        try:
            delay_ms = int(delay_ms)
        except (TypeError, ValueError):
            delay_ms = 0

        delay_ms = max(0, min(delay_ms, 300_000))

        if delay_ms:
            await asyncio.sleep(delay_ms / 1000)