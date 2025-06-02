from typing import Any, Optional

from .error_code import ERROR_MESSAGE_MAP, ErrorCode


class APIException(Exception):
    """API exception class."""

    def __init__(
        self,
        error_code: ErrorCode | str,
        message: str | None = None,
        detail: Any = None,
    ):
        self.error_code = error_code
        self.message = message
        self.detail = detail

        # If ErrorCode enum, use default message
        if isinstance(error_code, ErrorCode) and message is None:
            self.message = ERROR_MESSAGE_MAP.get(error_code, str(error_code))
        elif message is None:
            self.message = str(error_code)


class NotFoundException(APIException):
    """Resource not found exception (404)."""

    def __init__(self, message: str | None = None, detail: Any = None):
        super().__init__(
            error_code=ErrorCode.NOT_FOUND,
            message=message or "Resource not found",
            detail=detail,
        )
        self.status_code = 404


class UnauthorizedException(APIException):
    """Authentication failed exception (401)."""

    def __init__(self, message: str | None = None, detail: Any = None):
        super().__init__(
            error_code=ErrorCode.UNAUTHORIZED,
            message=message or "Authentication failed",
            detail=detail,
        )
        self.status_code = 401


class ForbiddenException(APIException):
    """Access denied exception (403)."""

    def __init__(self, message: str | None = None, detail: Any = None):
        super().__init__(
            error_code=ErrorCode.FORBIDDEN,
            message=message or "Access denied",
            detail=detail,
        )
        self.status_code = 403


class ValidationException(APIException):
    """Data validation failed exception (422)."""

    def __init__(self, message: str | None = None, detail: Any = None):
        super().__init__(
            error_code=ErrorCode.VALIDATION_ERROR,
            message=message or "Data validation failed",
            detail=detail,
        )
        self.status_code = 422


class ConflictException(APIException):
    """Resource conflict exception (409)."""

    def __init__(self, message: str | None = None, detail: Any = None):
        super().__init__(
            error_code=ErrorCode.CONFLICT,
            message=message or "Resource conflict",
            detail=detail,
        )
        self.status_code = 409


class BadRequestException(APIException):
    """Bad request exception (400)."""

    def __init__(self, message: str | None = None, detail: Any = None):
        super().__init__(
            error_code=ErrorCode.BAD_REQUEST,
            message=message or "Bad request",
            detail=detail,
        )
        self.status_code = 400


class DatabaseException(APIException):
    """Database operation failed exception (500)."""

    def __init__(self, message: str | None = None, detail: Any = None):
        super().__init__(
            error_code=ErrorCode.DATABASE_ERROR,
            message=message or "Database operation failed",
            detail=detail,
        )
        self.status_code = 500


class InternalServerException(APIException):
    """Internal server error exception (500)."""

    def __init__(self, message: str | None = None, detail: Any = None):
        super().__init__(
            error_code=ErrorCode.INTERNAL_ERROR,
            message=message or "Internal server error",
            detail=detail,
        )
        self.status_code = 500
