import time
from uuid import uuid4

from starlette.types import ASGIApp, Message, Receive, Scope, Send


REQUEST_ID_HEADER = "X-Request-ID"


class RequestContextMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = self._get_request_id(scope)
        scope.setdefault("state", {})
        scope["state"]["request_id"] = request_id
        scope["state"]["request_started_at"] = time.perf_counter()

        async def send_with_request_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append(
                    (
                        REQUEST_ID_HEADER.lower().encode("latin-1"),
                        request_id.encode("latin-1"),
                    )
                )
                message["headers"] = headers

            await send(message)

        await self.app(scope, receive, send_with_request_id)

    @staticmethod
    def _get_request_id(scope: Scope) -> str:
        for key, value in scope.get("headers", []):
            if key.lower() == REQUEST_ID_HEADER.lower().encode("latin-1"):
                try:
                    request_id = value.decode("latin-1").strip()
                except UnicodeDecodeError:
                    break

                if request_id and len(request_id) <= 100:
                    return request_id

                break

        return str(uuid4())