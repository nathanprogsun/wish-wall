"""
Authentication decorators for protecting routes using JWT tokens.
"""

from collections.abc import Callable
from functools import wraps
from typing import Any, Optional

from flask import current_app, request

from app.common.database import get_db_session
from app.common.exception import (
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
)
from app.model.user import User
from app.util.jwt_utils import (
    extract_token_from_header,
    validate_access_token,
    validate_remember_token,
    generate_access_token,
    generate_remember_token as jwt_generate_remember_token,
)


def login_required(f: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to require user authentication using JWT tokens.

    This decorator checks for a valid JWT token in the Authorization header.
    The user object is passed as the first argument to the decorated function.
    """

    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        try:
            # Extract token from Authorization header
            auth_header = request.headers.get("Authorization")
            token = extract_token_from_header(auth_header)

            # Debug token info in development
            if current_app.debug:
                current_app.logger.debug(f"Authorization header: {auth_header}")
                current_app.logger.debug(f"Extracted token: {token is not None}")

            user_id = None
            if token:
                # Try to validate as access token first
                user_id = validate_access_token(token)
                
                # If not valid as access token, try remember token
                if not user_id:
                    user_id = validate_remember_token(token)
                    if user_id and current_app.debug:
                        current_app.logger.debug(f"Validated remember token for user: {user_id}")

            if not user_id:
                raise UnauthorizedException("Authentication required, please login")

            # Load current user
            with get_db_session() as db_session:
                current_user = db_session.query(User).filter(User.id == user_id).first()
                if not current_user:
                    raise NotFoundException("User not found, please register")

                # Pass current_user as first argument
                return f(current_user, *args, **kwargs)

        except (UnauthorizedException, NotFoundException):
            raise
        except Exception as e:
            current_app.logger.error(f"Authentication error: {e!s}")
            raise UnauthorizedException("Authentication required, please login")

    return decorated_function


def admin_required(f: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to require admin privileges.

    Note: This is a placeholder for future admin functionality.
    Currently just checks for valid authentication.
    """

    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        try:
            # Extract token from Authorization header
            auth_header = request.headers.get("Authorization")
            token = extract_token_from_header(auth_header)

            user_id = None
            if token:
                user_id = validate_access_token(token)
                if not user_id:
                    user_id = validate_remember_token(token)

            if not user_id:
                raise UnauthorizedException("Authentication required, please login")

            with get_db_session() as db_session:
                current_user = db_session.query(User).filter(User.id == user_id).first()
                if not current_user:
                    raise NotFoundException("User not found")

                # TODO: Add admin role check when implementing user roles
                # if not current_user.is_admin:
                #     raise ForbiddenException("Admin access required")

                return f(current_user, *args, **kwargs)

        except (UnauthorizedException, NotFoundException, ForbiddenException):
            raise
        except Exception as e:
            current_app.logger.error(f"Admin authentication error: {e!s}")
            raise ForbiddenException("Admin access required")

    return decorated_function


def get_current_user() -> User | None:
    """
    Get current authenticated user from JWT token.

    Returns:
        User instance if authenticated, None otherwise
    """
    try:
        auth_header = request.headers.get("Authorization")
        token = extract_token_from_header(auth_header)
        
        if not token:
            return None
        
        user_id = validate_access_token(token)
        if not user_id:
            user_id = validate_remember_token(token)
        
        if user_id:
            with get_db_session() as db_session:
                return db_session.query(User).filter(User.id == user_id).first()
    except Exception as e:
        current_app.logger.warning(f"Failed to get current user: {e}")
    
    return None


# Legacy function for backwards compatibility - now generates JWT token
def generate_remember_token(user_id: str) -> str:
    """
    Generate a remember me JWT token for the user.

    Args:
        user_id: User ID

    Returns:
        JWT remember token string
    """
    return jwt_generate_remember_token(user_id)
