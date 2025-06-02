"""
Simplified error code system.
"""

from enum import StrEnum
from typing import Dict


class ErrorCode(StrEnum):
    """Universal error codes."""

    # Client errors (4xx)
    BAD_REQUEST = "BAD_REQUEST"  # 400 - Bad request format
    UNAUTHORIZED = "UNAUTHORIZED"  # 401 - Authentication failed
    FORBIDDEN = "FORBIDDEN"  # 403 - Access denied
    NOT_FOUND = "NOT_FOUND"  # 404 - Resource not found
    CONFLICT = "CONFLICT"  # 409 - Resource conflict
    VALIDATION_ERROR = "VALIDATION_ERROR"  # 422 - Data validation failed

    # Server errors (5xx)
    INTERNAL_ERROR = "INTERNAL_ERROR"  # 500 - Internal server error
    DATABASE_ERROR = "DATABASE_ERROR"  # 500 - Database error
    EXTERNAL_ERROR = "EXTERNAL_ERROR"  # 500 - External service error


# Error code to default message mapping
ERROR_MESSAGE_MAP: dict[ErrorCode, str] = {
    ErrorCode.BAD_REQUEST: "Bad request format",
    ErrorCode.UNAUTHORIZED: "Authentication failed",
    ErrorCode.FORBIDDEN: "Access denied",
    ErrorCode.NOT_FOUND: "Resource not found",
    ErrorCode.CONFLICT: "Resource conflict",
    ErrorCode.VALIDATION_ERROR: "Data validation failed",
    ErrorCode.INTERNAL_ERROR: "Internal server error",
    ErrorCode.DATABASE_ERROR: "Database error",
    ErrorCode.EXTERNAL_ERROR: "External service error",
}
