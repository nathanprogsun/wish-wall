"""
Authentication decorators for protecting routes using Flask sessions.
"""

from collections.abc import Callable
from functools import wraps
from typing import Any, Optional

from flask import current_app, jsonify, make_response, request, session

from app.common.database import get_db_session
from app.common.exception import (
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
)
from app.model.user import User


def login_required(f: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to require user authentication using sessions.

    This decorator checks for a valid session and loads the current user.
    The user object is passed as the first argument to the decorated function.
    """

    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        try:
            # Check if user is logged in via session
            user_id = session.get("user_id")

            # Debug session info in development
            if current_app.debug:
                current_app.logger.debug(f"Session data: {dict(session)}")
                current_app.logger.debug(f"User ID from session: {user_id}")

            if not user_id:
                # Check for remember me cookie
                remember_token = request.cookies.get(
                    current_app.config["REMEMBER_COOKIE_NAME"]
                )
                if remember_token:
                    user_id = _validate_remember_token(remember_token)
                    if user_id:
                        # Restore session from remember token
                        session["user_id"] = user_id
                        session.permanent = True
                        if current_app.debug:
                            current_app.logger.debug(
                                f"Restored session from remember token for user: {user_id}"
                            )
                    else:
                        # Invalid remember token, clear it
                        response = make_response(
                            jsonify({"error": "Authentication required"}), 401
                        )
                        response.set_cookie(
                            current_app.config["REMEMBER_COOKIE_NAME"],
                            "",
                            expires=0,
                            httponly=True,
                            secure=current_app.config.get(
                                "REMEMBER_COOKIE_SECURE", False
                            ),
                            samesite="Lax",
                        )
                        return response

            if not user_id:
                raise ForbiddenException("Authentication required, please login")

            # Load current user
            db_session = get_db_session()
            current_user = db_session.query(User).filter(User.id == user_id).first()
            if not current_user:
                # User not found, clear session
                session.clear()
                raise NotFoundException("User not found, please register")

            # Pass current_user as first argument
            return f(current_user, *args, **kwargs)

        except Exception as e:
            current_app.logger.error(f"Authentication error: {e!s}")
            raise ForbiddenException("Authentication required, please login")

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
            user_id = session.get("user_id")

            if not user_id:
                raise ForbiddenException("Authentication required, please login")

            db_session = get_db_session()
            current_user = db_session.query(User).filter(User.id == user_id).first()
            if not current_user:
                session.clear()
                return jsonify({"error": "User not found"}), 404

            # TODO: Add admin role check when implementing user roles
            # if not current_user.is_admin:
            #     return jsonify({'error': 'Admin access required'}), 403

            return f(current_user, *args, **kwargs)

        except Exception as e:
            current_app.logger.error(f"Admin authentication error: {e!s}")
            raise ForbiddenException("Admin access required")

    return decorated_function


def get_current_user() -> User | None:
    """
    Get current authenticated user from session.

    Returns:
        User instance if authenticated, None otherwise
    """
    user_id = session.get("user_id")
    if user_id:
        db_session = get_db_session()
        return db_session.query(User).filter(User.id == user_id).first()
    return None


def generate_remember_token(user_id: str) -> str:
    """
    Generate a remember me token for the user.

    Args:
        user_id: User ID

    Returns:
        Remember token string
    """
    from itsdangerous import URLSafeTimedSerializer

    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps({"user_id": user_id})


def _validate_remember_token(token: str) -> str | None:
    """
    Validate a remember me token and return user ID.

    Args:
        token: Remember token to validate

    Returns:
        User ID if valid, None otherwise
    """
    try:
        from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

        serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        max_age = current_app.config["REMEMBER_COOKIE_DURATION"].total_seconds()

        data = serializer.loads(token, max_age=max_age)
        user_id = data.get("user_id")
        return user_id if isinstance(user_id, str) else None

    except (BadSignature, SignatureExpired, KeyError):
        return None
