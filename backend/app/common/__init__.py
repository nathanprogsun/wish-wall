"""
Common utilities and shared functionality.
"""

from .error_code import ErrorCode
from .exception import (
    APIException,
    BadRequestException,
    ConflictException,
    DatabaseException,
    ForbiddenException,
    InternalServerException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)
from .logger import get_logger
from .response import api_response, created_response, error_response, success_response

__all__ = [
    "APIException",
    "BadRequestException",
    "ConflictException",
    "DatabaseException",
    "ErrorCode",
    "ForbiddenException",
    "InternalServerException",
    # Specific exceptions
    "NotFoundException",
    "UnauthorizedException",
    "ValidationException",
    "api_response",
    "created_response",
    "error_response",
    "get_logger",
    "success_response",
]
