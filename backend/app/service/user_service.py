from typing import Any

from flask import current_app, make_response, session

from app.common.database import get_db_session
from app.common.exception import (
    NotFoundException,
    UnauthorizedException,
)
from app.model.user import User
from app.schema.user import (
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.util.auth_decorators import generate_remember_token


class UserService:
    """Service for user-related operations."""

    @staticmethod
    def register(request: UserRegisterRequest) -> UserResponse:
        """Register a new user."""
        user = User.create_user(
            username=request.username,
            email=request.email,
            password=request.password,
        )
        db_session = get_db_session()
        db_session.commit()
        return UserResponse.from_model(user)

    @staticmethod
    def login(
        request: UserLoginRequest,
    ) -> tuple[UserResponse, Any | None]:
        """Authenticate user and create session."""
        db_session = get_db_session()

        # Find user by username or email
        user = (
            db_session.query(User)
            .filter((User.username == request.login) | (User.email == request.login))
            .first()
        )

        if not user or not user.check_password(request.password):
            raise UnauthorizedException("Invalid username or password")

        # Update last login
        user.update_last_login()
        db_session.commit()

        # Create session
        session["user_id"] = user.id
        session.permanent = request.remember_me

        # Handle remember me functionality
        response = None
        if request.remember_me:
            remember_token = generate_remember_token(str(user.id))
            response = make_response()
            response.set_cookie(
                current_app.config["REMEMBER_COOKIE_NAME"],
                remember_token,
                max_age=int(
                    current_app.config["REMEMBER_COOKIE_DURATION"].total_seconds()
                ),
                httponly=current_app.config.get("REMEMBER_COOKIE_HTTPONLY", True),
                secure=current_app.config.get("REMEMBER_COOKIE_SECURE", False),
                samesite=current_app.config.get("REMEMBER_COOKIE_SAMESITE", "Lax"),
                domain=current_app.config.get("REMEMBER_COOKIE_DOMAIN"),
            )

        return UserResponse.from_model(user), response

    @staticmethod
    def logout_user() -> None:
        """Logout current user."""
        session.clear()

    @staticmethod
    def get_user_profile(user_id: str) -> UserResponse:
        """Get user profile by ID."""
        db_session = get_db_session()
        user = db_session.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundException("User not found")

        return UserResponse.from_model(user)
