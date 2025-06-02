"""
Validation decorators for request data validation using Pydantic.
"""

from collections.abc import Callable
from functools import wraps
from typing import Any

from flask import jsonify, request
from pydantic import BaseModel, ValidationError


def validate_json(model_class: type[BaseModel]) -> Callable:
    """
    Decorator to validate JSON request data using Pydantic schema.

    Args:
        model_class: Pydantic model class for validation

    Returns:
        Decorated function with validated data
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Get JSON data from request
                json_data = request.get_json()

                if json_data is None:
                    return jsonify({"error": "Invalid JSON data"}), 400

                # Validate using Pydantic model
                validated_data = model_class.model_validate(json_data)

                # Add validated data to kwargs
                kwargs["validated_data"] = validated_data
                return f(*args, **kwargs)

            except ValidationError as e:
                return jsonify(
                    {"error": "Validation failed", "details": e.errors()}
                ), 400

            except Exception as e:
                return jsonify({"error": f"Validation error: {e!s}"}), 400

        return decorated_function

    return decorator


def validate_query_params(model_class: type[BaseModel]) -> Callable:
    """
    Decorator to validate query parameters using Pydantic schema.

    Args:
        model_class: Pydantic model class for validation

    Returns:
        Decorated function with validated query parameters
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Get query parameters
                query_data = request.args.to_dict()

                # Validate using Pydantic model
                validated_data = model_class.model_validate(query_data)

                # Add validated data to kwargs
                kwargs["query_params"] = validated_data
                return f(*args, **kwargs)

            except ValidationError as e:
                return jsonify(
                    {
                        "error": "Query validation failed",
                        "details": e.errors(),
                    }
                ), 400

            except Exception as e:
                return jsonify({"error": f"Query validation error: {e!s}"}), 400

        return decorated_function

    return decorator
