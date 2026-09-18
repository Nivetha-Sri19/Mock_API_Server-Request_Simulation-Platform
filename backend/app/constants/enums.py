from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class APIStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class APIScope(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"


class ResponseScenario(str, Enum):
    SUCCESS = "success"
    VALIDATION_ERROR = "validation_error"
    UNAUTHORIZED = "unauthorized"
    NOT_FOUND = "not_found"
    SERVER_ERROR = "server_error"
    CUSTOM = "custom"


class PermissionType(str, Enum):
    VIEW = "view"
    EXECUTE = "execute"
    MANAGE = "manage"


class TokenType(str, Enum):
    ACCESS = "access"