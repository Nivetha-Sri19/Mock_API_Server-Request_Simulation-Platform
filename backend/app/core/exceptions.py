from typing import Any


class AppException(Exception):
    def __init__(
        self,
        status_code: int,
        detail: str | None = None,
        code: str | None = None,
        data: Any = None,
        message: str | None = None,
        error_code: str | None = None,
    ) -> None:
        final_message = message or detail or "Application error."
        final_code = error_code or code or "APP_ERROR"

        self.status_code = status_code
        self.detail = final_message
        self.message = final_message
        self.code = final_code
        self.error_code = final_code
        self.data = data

        super().__init__(final_message)


class BadRequestException(AppException):
    def __init__(
        self,
        detail: str = "Bad request.",
        code: str = "BAD_REQUEST",
        data: Any = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            status_code=400,
            detail=detail,
            code=code,
            data=data,
            **kwargs,
        )


class UnauthorizedException(AppException):
    def __init__(
        self,
        detail: str = "Unauthorized.",
        code: str = "UNAUTHORIZED",
        data: Any = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            status_code=401,
            detail=detail,
            code=code,
            data=data,
            **kwargs,
        )


class AuthenticationException(UnauthorizedException):
    def __init__(
        self,
        detail: str = "Authentication failed.",
        code: str = "AUTHENTICATION_ERROR",
        data: Any = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            detail=detail,
            code=code,
            data=data,
            **kwargs,
        )


class ForbiddenException(AppException):
    def __init__(
        self,
        detail: str = "Forbidden.",
        code: str = "FORBIDDEN",
        data: Any = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            status_code=403,
            detail=detail,
            code=code,
            data=data,
            **kwargs,
        )


class AuthorizationException(ForbiddenException):
    def __init__(
        self,
        detail: str = "Authorization failed.",
        code: str = "AUTHORIZATION_ERROR",
        data: Any = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            detail=detail,
            code=code,
            data=data,
            **kwargs,
        )


class NotFoundException(AppException):
    def __init__(
        self,
        detail: str = "Resource not found.",
        code: str = "NOT_FOUND",
        data: Any = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            status_code=404,
            detail=detail,
            code=code,
            data=data,
            **kwargs,
        )


class ConflictException(AppException):
    def __init__(
        self,
        detail: str = "Resource already exists.",
        code: str = "CONFLICT",
        data: Any = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            status_code=409,
            detail=detail,
            code=code,
            data=data,
            **kwargs,
        )


class ValidationException(AppException):
    def __init__(
        self,
        detail: str = "Validation failed.",
        code: str = "VALIDATION_ERROR",
        data: Any = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            status_code=422,
            detail=detail,
            code=code,
            data=data,
            **kwargs,
        )


class TooManyRequestsException(AppException):
    def __init__(
        self,
        detail: str = "Too many requests.",
        code: str = "TOO_MANY_REQUESTS",
        data: Any = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            status_code=429,
            detail=detail,
            code=code,
            data=data,
            **kwargs,
        )


class InternalServerException(AppException):
    def __init__(
        self,
        detail: str = "Internal server error.",
        code: str = "INTERNAL_SERVER_ERROR",
        data: Any = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            status_code=500,
            detail=detail,
            code=code,
            data=data,
            **kwargs,
        )