from typing import Any, Dict

from flask import current_app

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
from app.util.jwt_utils import (
    generate_access_token,
    generate_remember_token,
)


class UserService:
    """Service for user-related operations."""

    @staticmethod
    def register(request: UserRegisterRequest) -> UserResponse:
        """Register a new user."""
        with get_db_session() as db_session:
            if db_session.query(User).filter(User.username == request.username).first():
                raise ValueError("Username already exists")
            
            if db_session.query(User).filter(User.email == request.email).first():
                raise ValueError("Email already exists")
            
            # Create user directly in this session instead of using User.create_user
            user = User(
                username=request.username,
                email=request.email,
                password=request.password,
            )
            db_session.add(user)
            db_session.flush()  # Flush to get the user ID without committing
            
            # Create response while user is still attached to session
            user_response = UserResponse.from_model(user)
            # Session will commit automatically when exiting the with block
            return user_response

    @staticmethod
    def login(request: UserLoginRequest) -> Dict[str, Any]:
        """Authenticate user and return JWT tokens."""
        with get_db_session() as db_session:
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

            # Generate tokens
            access_token = generate_access_token(str(user.id), remember_me=request.remember_me)
            
            response_data = {
                "user": UserResponse.from_model(user),
                "access_token": access_token,
                "token_type": "Bearer"
            }
            
            # Add remember token if remember_me is True
            if request.remember_me:
                remember_token = generate_remember_token(str(user.id))
                response_data["remember_token"] = remember_token

            return response_data

    @staticmethod
    def logout_user() -> Dict[str, str]:
        """Logout current user (client-side token removal)."""
        return {"message": "Logged out successfully"}

    @staticmethod
    def get_user_profile(user_id: str) -> UserResponse:
        """Get user profile by ID."""
        with get_db_session() as db_session:
            user = db_session.query(User).filter(User.id == user_id).first()
            if not user:
                raise NotFoundException("User not found")

            return UserResponse.from_model(user)
