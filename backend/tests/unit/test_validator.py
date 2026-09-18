import pytest

from app.core.exceptions import ValidationException
from app.dynamic.validator import RequestValidator


@pytest.mark.asyncio
async def test_valid_request():
    validator = RequestValidator()
    await validator.validate(
        request_schema={
            "query_parameters": [{"name": "page", "type": "integer", "required": True}],
            "path_parameters": [{"name": "id", "type": "integer", "required": True}],
            "headers": [{"name": "x-api-key", "type": "string", "required": True}],
            "body_schema": {"name": {"type": "string", "required": True}},
        },
        query_parameters={"page": 1},
        path_parameters={"id": 10},
        headers={"x-api-key": "abc"},
        body={"name": "test"},
    )


@pytest.mark.asyncio
async def test_invalid_request():
    validator = RequestValidator()
    with pytest.raises(ValidationException):
        await validator.validate(
            request_schema={"query_parameters": [{"name": "page", "type": "integer", "required": True}]},
            query_parameters={},
            path_parameters={},
            headers={},
            body=None,
        )
