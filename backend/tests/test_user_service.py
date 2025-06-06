"""
Test suite for UserService functionality using function style.
"""

import pytest

from app.common.exception import (
    NotFoundException,
    UnauthorizedException,
)
from app.schema.user import (
    UserLoginRequest,
    UserRegisterRequest,
)
from app.service.user_service import UserService


# Registration Tests
def test_successful_registration(db_session):
    """Test successful user registration."""
    request = UserRegisterRequest(
        username="newuser123",
        email="newuser@example.com",
        password="NewPass123!",
    )

    response = UserService.register(request)

    assert response.username == "newuser123"
    assert response.email == "newuser@example.com"
    assert response.id is not None
    assert response.created_at is not None


def test_registration_duplicate_username(db_session):
    """Test registration with duplicate username."""
    # First create a user
    first_request = UserRegisterRequest(
        username="testuser123",
        email="first@example.com",
        password="NewPass123!",
    )
    UserService.register(first_request)

    # Now try to create another user with same username
    second_request = UserRegisterRequest(
        username="testuser123",  # Same username
        email="different@example.com",
        password="NewPass123!",
    )
    
    with pytest.raises(ValueError) as exc_info:
        UserService.register(second_request)

    assert "Username already exists" in str(exc_info.value)


def test_registration_duplicate_email(db_session):
    """Test registration with duplicate email."""
    # First create a user
    first_request = UserRegisterRequest(
        username="firstuser123",
        email="test@example.com",
        password="NewPass123!",
    )
    UserService.register(first_request)

    # Now try to create another user with same email
    second_request = UserRegisterRequest(
        username="differentuser123",
        email="test@example.com",  # Same email
        password="NewPass123!",
    )
    
    with pytest.raises(ValueError) as exc_info:
        UserService.register(second_request)

    assert "Email already exists" in str(exc_info.value)


def test_registration_invalid_username_format(db_session):
    """Test registration with invalid username format."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError) as exc_info:
        UserRegisterRequest(
            username="user_with_underscore",
            email="test@example.com",
            password="NewPass123!",
        )

    assert "Username can only contain letters and numbers" in str(exc_info.value)


def test_registration_invalid_password_complexity(db_session):
    """Test registration with invalid password complexity."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError) as exc_info:
        UserRegisterRequest(
            username="validuser123",
            email="test@example.com",
            password="weakpass",  # Missing uppercase, digits, special chars
        )

    assert "Password must contain at least one uppercase letter" in str(exc_info.value)


# Authentication Tests
def test_successful_login_with_username(app, test_user):
    """Test successful login with username."""
    with app.app_context():
        # Access all attributes before the session context to avoid detached instance
        username = test_user.username
        email = test_user.email
        request = UserLoginRequest(
            login=username, password="TestPass123!", remember_me=False
        )

        response = UserService.login(request)

        assert response["user"].username == username
        assert response["user"].email == email
        assert response["access_token"] is not None
        assert response["token_type"] == "Bearer"
        assert "remember_token" not in response  # No remember me


def test_successful_login_with_email(app, test_user):
    """Test successful login with email."""
    with app.app_context():
        # Access email before the session context to avoid detached instance
        email = test_user.email
        request = UserLoginRequest(
            login=email, password="TestPass123!", remember_me=False
        )

        response = UserService.login(request)

        assert response["user"].email == email
        assert response["access_token"] is not None


def test_successful_login_with_remember_me(app, test_user):
    """Test successful login with remember me."""
    with app.app_context():
        # Access username before the session context to avoid detached instance
        username = test_user.username
        request = UserLoginRequest(
            login=username, password="TestPass123!", remember_me=True
        )

        response = UserService.login(request)

        assert response["user"].username == username
        assert response["access_token"] is not None
        assert response["remember_token"] is not None  # Should have remember me token


def test_invalid_username_login(app):
    """Test login with invalid username."""
    with app.app_context():
        request = UserLoginRequest(
            login="nonexistentuser", password="TestPass123!", remember_me=False
        )

        with pytest.raises(UnauthorizedException) as exc_info:
            UserService.login(request)

        assert "Invalid username or password" in str(exc_info.value)


def test_invalid_password_login(app, test_user):
    """Test login with invalid password."""
    with app.app_context():
        # Access username before the session context to avoid detached instance
        username = test_user.username
        request = UserLoginRequest(
            login=username, password="wrongpassword", remember_me=False
        )

        with pytest.raises(UnauthorizedException) as exc_info:
            UserService.login(request)

        assert "Invalid username or password" in str(exc_info.value)


# Profile Tests
def test_get_user_profile_success(app, test_user):
    """Test successful user profile retrieval."""
    with app.app_context():
        # Access attributes before the session context to avoid detached instance
        user_id = test_user.id
        username = test_user.username
        email = test_user.email
        
        response = UserService.get_user_profile(user_id)

        assert response.username == username
        assert response.email == email
        assert response.id == user_id


def test_get_user_profile_not_found(app):
    """Test user profile retrieval with invalid ID."""
    with app.app_context():
        with pytest.raises(NotFoundException) as exc_info:
            UserService.get_user_profile("invalid-user-id")

        assert "User not found" in str(exc_info.value)
