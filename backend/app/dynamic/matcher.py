import re
from dataclasses import dataclass
from typing import Any
from uuid import UUID
from urllib.parse import unquote

from app.core.exceptions import NotFoundException
from app.dynamic.path_converter import PathConverter


@dataclass(frozen=True)
class MatchedEndpoint:
    api_id: UUID
    api_version_id: UUID
    owner_id: UUID
    name: str
    base_path: str
    version: str
    is_private: bool
    path_parameters: dict[str, str]


class EndpointMatcher:
    def __init__(self, definitions: list[dict[str, Any]]) -> None:
        self.definitions = definitions

    def match(
        self,
        *,
        method: str,
        path: str,
    ) -> MatchedEndpoint:
        normalized_method = method.upper()
        normalized_path = PathConverter.normalize(path)

        candidates: list[tuple[int, MatchedEndpoint]] = []

        for definition in self.definitions:
            if not definition.get("is_active", False):
                continue

            configured_method = str(
                definition.get("http_method", ""),
            ).upper()

            if configured_method != normalized_method:
                continue

            base_path = PathConverter.normalize(
                str(definition.get("base_path", "")),
            )

            parameter_names = PathConverter.extract_parameters(
                base_path,
            )

            pattern = self._build_pattern(
                base_path,
            )

            match = pattern.fullmatch(normalized_path)

            if not match:
                continue

            path_parameters = {
                name: unquote(value)
                for name, value in match.groupdict().items()
                if value is not None
            }

            matched = MatchedEndpoint(
                api_id=UUID(str(definition["api_id"])),
                api_version_id=UUID(
                    str(definition["api_version_id"]),
                ),
                owner_id=UUID(
                    str(definition["owner_id"]),
                ),
                name=str(definition.get("name", "")),
                base_path=base_path,
                version=str(definition.get("version", "")),
                is_private=bool(
                    definition.get("is_private", False),
                ),
                path_parameters=path_parameters,
            )

            static_segments = sum(
                1
                for segment in base_path.split("/")
                if segment and not self._is_parameter(segment)
            )

            candidates.append(
                (
                    static_segments,
                    matched,
                ),
            )

        if not candidates:
            raise NotFoundException(
                message="Mock endpoint not found",
                error_code="MOCK_ENDPOINT_NOT_FOUND",
            )

        candidates.sort(
            key=lambda item: (
                item[0],
                -len(item[1].path_parameters),
                len(item[1].base_path),
            ),
            reverse=True,
        )

        return candidates[0][1]

    @staticmethod
    def _is_parameter(segment: str) -> bool:
        return bool(
            re.fullmatch(
                r"\{[a-zA-Z_][a-zA-Z0-9_]*\}",
                segment,
            ),
        )

    @classmethod
    def _build_pattern(cls, base_path: str) -> re.Pattern[str]:
        segments = base_path.split("/")[1:]

        if not segments:
            return re.compile(r"^/$")

        pattern_segments: list[str] = []

        for segment in segments:
            if cls._is_parameter(segment):
                parameter_name = segment[1:-1]

                pattern_segments.append(
                    rf"(?P<{parameter_name}>[^/]+)",
                )
            else:
                pattern_segments.append(
                    re.escape(segment),
                )

        return re.compile(
            r"^/" + "/".join(pattern_segments) + r"/?$",
        )