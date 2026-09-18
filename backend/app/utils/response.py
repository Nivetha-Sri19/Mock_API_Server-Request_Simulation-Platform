from typing import Any

def success_response(message: str, data: Any = None) -> dict[str, Any]:
    response = {"success": True, "message": message}
    if data is not None:
        response["data"] = data
    return response
