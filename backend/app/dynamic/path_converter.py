import re


_PATH_PARAMETER_PATTERN = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")


class PathConverter:
    @staticmethod
    def normalize(path: str) -> str:
        path = path.strip()

        if not path:
            return "/"

        if not path.startswith("/"):
            path = f"/{path}"

        path = re.sub(r"/+", "/", path)

        if len(path) > 1 and path.endswith("/"):
            path = path.rstrip("/")

        return path

    @staticmethod
    def extract_parameters(path: str) -> list[str]:
        normalized_path = PathConverter.normalize(path)

        parameters = _PATH_PARAMETER_PATTERN.findall(
            normalized_path,
        )

        if len(parameters) != len(set(parameters)):
            raise ValueError(
                "Path parameter names must be unique",
            )

        return parameters

    @staticmethod
    def is_valid(path: str) -> bool:
        try:
            normalized_path = PathConverter.normalize(path)

            if normalized_path == "/":
                return True

            segments = normalized_path.split("/")[1:]

            for segment in segments:
                if not segment:
                    return False

                parameters = _PATH_PARAMETER_PATTERN.findall(segment)

                if parameters:
                    if len(parameters) != 1:
                        return False

                    if segment != f"{{{parameters[0]}}}":
                        return False

            return True

        except (TypeError, ValueError):
            return False

    @staticmethod
    def to_fastapi_path(path: str) -> str:
        normalized_path = PathConverter.normalize(path)

        if not PathConverter.is_valid(normalized_path):
            raise ValueError(
                f"Invalid API path: {path}",
            )

        return normalized_path

    @staticmethod
    def build_path(
        base_path: str,
        parameters: dict[str, object] | None = None,
    ) -> str:
        path = PathConverter.normalize(base_path)

        if not parameters:
            return path

        def replace_parameter(match: re.Match[str]) -> str:
            name = match.group(1)

            if name not in parameters:
                return match.group(0)

            value = str(parameters[name]).strip()

            if not value:
                raise ValueError(
                    f"Path parameter '{name}' cannot be empty",
                )

            return value.strip("/")

        return _PATH_PARAMETER_PATTERN.sub(
            replace_parameter,
            path,
        )