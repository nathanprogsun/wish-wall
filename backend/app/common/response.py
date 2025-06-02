"""
Standardized API response system.
"""

from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

from flask import Response, jsonify
from pydantic import BaseModel

from .error_code import ERROR_MESSAGE_MAP, ErrorCode


class ErrorInfo(BaseModel):
    """Error information model."""

    type: str
    message: str


class APIResponse(BaseModel):
    """Standard API response model."""

    status: int
    data: list | dict | Any | None = None
    error: ErrorInfo | None = None


def api_response(
    status: int | None = HTTPStatus.OK.value,
    data: list | dict | Any = None,
    error_code: ErrorCode | str | None = None,
    error_message: str | None = None,
) -> Response:
    """
    Create standard API response.

    Args:
        status: HTTP status code (defaults to 200 for success, auto-inferred for errors)
        data: Response data (for success responses)
        error_code: Error code (for error responses)
        error_message: Custom error message

    Returns:
        Flask Response object

    Examples:
        # Success responses
        api_response(data={"id": 1})  # status=200, data={"id": 1}
        api_response(status=201, data={"id": 1})  # status=201, data={"id": 1}

        # Error responses
        api_response(status=404, error_code=ErrorCode.NOT_FOUND)
        api_response(status=400, error_code="CUSTOM_ERROR", error_message="Custom message")
    """
    # Build error info
    error_info = None
    if error_code is not None:
        error_info = ErrorInfo(
            type=str(error_code),
            message=error_message
            if error_message
            else ERROR_MESSAGE_MAP.get(error_code, str(error_code)),
        )

    # Convert Pydantic models
    if hasattr(data, "model_dump") and callable(data.model_dump):
        data = data.model_dump()
    elif hasattr(data, "dict") and callable(data.dict):
        data = data.dict()

    # Error responses have no data
    if error_info:
        data = None

    # Build response
    content = APIResponse(
        status=status,
        data=data,
        error=error_info,
    ).model_dump()

    response = jsonify(content)
    response.status_code = status
    return response


def success_response(
    data: list | dict | Any = None,
    status: int = HTTPStatus.OK.value,
) -> Response:
    """Create success response."""
    return api_response(status=status, data=data)


def error_response(
    error_code: ErrorCode | str,
    message: str | None = None,
    status: int | None = HTTPStatus.INTERNAL_SERVER_ERROR.value,
) -> Response:
    """Create error response."""
    return api_response(
        status=status,
        error_code=error_code,
        error_message=message,
    )


def created_response(
    data: list | dict | Any = None,
) -> Response:
    """Create 201 response."""
    return api_response(status=HTTPStatus.CREATED.value, data=data)
