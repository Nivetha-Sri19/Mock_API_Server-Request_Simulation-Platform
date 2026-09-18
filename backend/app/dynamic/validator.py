from typing import Any

from app.core.exceptions import ValidationException


class RequestValidator:
    SUPPORTED_TYPES = {
        "string",
        "str",
        "integer",
        "int",
        "number",
        "float",
        "boolean",
        "bool",
        "object",
        "array",
        "null",
    }

    async def validate(
        self,
        *,
        request_schema: dict[str, Any],
        query_parameters: dict[str, Any],
        path_parameters: dict[str, Any],
        headers: dict[str, Any],
        body: Any,
    ) -> None:
        if not request_schema:
            return

        errors: list[dict[str, Any]] = []

        errors.extend(
            self._validate_parameters(
                request_schema.get(
                    "query_parameters",
                    [],
                ),
                query_parameters,
                "query",
            )
        )

        errors.extend(
            self._validate_parameters(
                request_schema.get(
                    "path_parameters",
                    [],
                ),
                path_parameters,
                "path",
            )
        )

        errors.extend(
            self._validate_parameters(
                request_schema.get(
                    "headers",
                    [],
                ),
                headers,
                "header",
            )
        )

        body_schema = request_schema.get(
            "body_schema"
        )

        if body_schema is not None:
            errors.extend(
                self._validate_body(
                    body_schema,
                    body,
                )
            )

        if errors:
            raise ValidationException(
                detail="Request validation failed",
                code="REQUEST_VALIDATION_FAILED",
                data=errors,
            )

    def _validate_parameters(
        self,
        definitions: Any,
        values: dict[str, Any],
        source: str,
    ) -> list[dict[str, Any]]:

        if not isinstance(definitions, list):
            return [
                {
                    "source": source,
                    "field": source,
                    "message": (
                        "Parameter definitions "
                        "must be a list"
                    ),
                }
            ]

        normalized = {
            str(key).lower(): value
            for key, value in values.items()
        }

        errors: list[dict[str, Any]] = []

        for definition in definitions:

            if not isinstance(
                definition,
                dict,
            ):
                errors.append(
                    {
                        "source": source,
                        "field": source,
                        "message": (
                            "Invalid parameter "
                            "definition"
                        ),
                    }
                )
                continue

            name = str(
                definition.get(
                    "name",
                    "",
                )
            ).strip()

            if not name:
                errors.append(
                    {
                        "source": source,
                        "field": source,
                        "message": (
                            "Parameter name "
                            "is required"
                        ),
                    }
                )
                continue

            value = normalized.get(
                name.lower()
            )

            if value is None:

                if (
                    definition.get(
                        "default"
                    )
                    is not None
                ):
                    value = definition[
                        "default"
                    ]

                elif bool(
                    definition.get(
                        "required",
                        False,
                    )
                ):
                    errors.append(
                        {
                            "source": source,
                            "field": name,
                            "message": (
                                "Field is required"
                            ),
                        }
                    )
                    continue

                else:
                    continue

            error = self._type_error(
                value,
                str(
                    definition.get(
                        "type",
                        "string",
                    )
                ).lower(),
            )

            if error:
                errors.append(
                    {
                        "source": source,
                        "field": name,
                        "message": error,
                    }
                )

        return errors

    def _validate_body(
        self,
        schema: Any,
        body: Any,
    ) -> list[dict[str, Any]]:

        if not isinstance(schema, dict):
            return [
                {
                    "source": "body",
                    "field": "body",
                    "message": (
                        "Body schema must "
                        "be an object"
                    ),
                }
            ]

        if body is None:
            return [
                {
                    "source": "body",
                    "field": "body",
                    "message": (
                        "Request body is required"
                    ),
                }
            ]

        errors: list[dict[str, Any]] = []

        if self._looks_like_json_schema(
            schema
        ):
            self._validate_json_schema(
                schema,
                body,
                ("body",),
                errors,
            )
        else:

            if not isinstance(
                body,
                dict,
            ):
                return [
                    {
                        "source": "body",
                        "field": "body",
                        "message": (
                            "Request body must "
                            "be a JSON object"
                        ),
                    }
                ]

            for name, definition in schema.items():

                if not isinstance(
                    definition,
                    dict,
                ):
                    definition = {
                        "type": str(
                            definition
                        )
                    }

                if name not in body:

                    if definition.get(
                        "required",
                        False,
                    ):
                        errors.append(
                            {
                                "source": "body",
                                "field": name,
                                "message": (
                                    "Field is required"
                                ),
                            }
                        )

                    continue

                error = self._type_error(
                    body[name],
                    str(
                        definition.get(
                            "type",
                            "string",
                        )
                    ).lower(),
                )

                if error:
                    errors.append(
                        {
                            "source": "body",
                            "field": name,
                            "message": error,
                        }
                    )

        return errors

    def _validate_json_schema(
        self,
        schema: dict[str, Any],
        value: Any,
        location: tuple[str, ...],
        errors: list[dict[str, Any]],
    ) -> None:

        if not isinstance(
            schema,
            dict,
        ):
            errors.append(
                {
                    "source": "body",
                    "field": ".".join(
                        location
                    ),
                    "message": (
                        "Invalid JSON schema"
                    ),
                }
            )
            return

        expected = schema.get("type")

        if expected:
            error = self._type_error(
                value,
                str(expected).lower(),
            )

            if error:
                errors.append(
                    {
                        "source": "body",
                        "field": ".".join(
                            location
                        ),
                        "message": error,
                    }
                )
                return

        if expected == "object":

            properties = schema.get(
                "properties",
                {},
            )

            required = schema.get(
                "required",
                [],
            )

            if isinstance(
                required,
                list,
            ):
                for name in required:

                    if name not in value:
                        errors.append(
                            {
                                "source": "body",
                                "field": ".".join(
                                    location
                                    + (str(name),)
                                ),
                                "message": (
                                    "Field is required"
                                ),
                            }
                        )

            if isinstance(
                properties,
                dict,
            ):
                for name, child in (
                    properties.items()
                ):

                    if name in value:
                        self._validate_json_schema(
                            child,
                            value[name],
                            location
                            + (str(name),),
                            errors,
                        )

        elif expected == "array":

            item_schema = schema.get(
                "items"
            )

            if isinstance(
                item_schema,
                dict,
            ):
                for index, item in enumerate(
                    value
                ):
                    self._validate_json_schema(
                        item_schema,
                        item,
                        location
                        + (str(index),),
                        errors,
                    )

    @staticmethod
    def _looks_like_json_schema(
        schema: dict[str, Any],
    ) -> bool:

        return any(
            key in schema
            for key in (
                "type",
                "properties",
                "required",
                "items",
                "additionalProperties",
            )
        )

    def _type_error(
        self,
        value: Any,
        expected: str,
    ) -> str | None:

        if expected not in self.SUPPORTED_TYPES:
            return (
                f"Unsupported parameter type: "
                f"{expected}"
            )

        valid = {
            "string": isinstance(
                value,
                str,
            ),
            "str": isinstance(
                value,
                str,
            ),
            "integer": (
                isinstance(
                    value,
                    int,
                )
                and not isinstance(
                    value,
                    bool,
                )
            ),
            "int": (
                isinstance(
                    value,
                    int,
                )
                and not isinstance(
                    value,
                    bool,
                )
            ),
            "number": (
                isinstance(
                    value,
                    (int, float),
                )
                and not isinstance(
                    value,
                    bool,
                )
            ),
            "float": (
                isinstance(
                    value,
                    (int, float),
                )
                and not isinstance(
                    value,
                    bool,
                )
            ),
            "boolean": isinstance(
                value,
                bool,
            ),
            "bool": isinstance(
                value,
                bool,
            ),
            "object": isinstance(
                value,
                dict,
            ),
            "array": isinstance(
                value,
                list,
            ),
            "null": value is None,
        }

        if not valid[expected]:
            return (
                f"Value must be of type "
                f"{expected}"
            )

        return None