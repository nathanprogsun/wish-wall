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
    from pydantic import ValidationError

    # First create a user
    first_request = UserRegisterRequest(
        username="testuser123",
        email="first@example.com",
        password="NewPass123!",
    )
    UserService.register(first_request)

    # Now try to create another user with same username
    with pytest.raises(ValidationError) as exc_info:
        UserRegisterRequest(
            username="testuser123",  # Same username
            email="different@example.com",
            password="NewPass123!",
        )

    assert "Username already exists" in str(exc_info.value)


def test_registration_duplicate_email(db_session):
    """Test registration with duplicate email."""
    from pydantic import ValidationError

    # First create a user
    first_request = UserRegisterRequest(
        username="firstuser123",
        email="test@example.com",
        password="NewPass123!",
    )
    UserService.register(first_request)

    # Now try to create another user with same email
    with pytest.raises(ValidationError) as exc_info:
        UserRegisterRequest(
            username="differentuser123",
            email="test@example.com",  # Same email
            password="NewPass123!",
        )

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
        request = UserLoginRequest(
            login=test_user.username, password="TestPass123!", remember_me=False
        )

        response, cookie_response = UserService.login(request)

        assert response.username == test_user.username
        assert response.email == test_user.email
        assert cookie_response is None  # No remember me


def test_successful_login_with_email(app, test_user):
    """Test successful login with email."""
    with app.app_context():
        request = UserLoginRequest(
            login=test_user.email, password="TestPass123!", remember_me=False
        )

        response, cookie_response = UserService.login(request)

        assert response.email == test_user.email


def test_successful_login_with_remember_me(app, test_user):
    """Test successful login with remember me."""
    with app.app_context():
        request = UserLoginRequest(
            login=test_user.username, password="TestPass123!", remember_me=True
        )

        response, cookie_response = UserService.login(request)

        assert response.username == test_user.username
        assert cookie_response is not None  # Should have remember me cookie


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
        request = UserLoginRequest(
            login=test_user.username, password="wrongpassword", remember_me=False
        )

        with pytest.raises(UnauthorizedException) as exc_info:
            UserService.login(request)

        assert "Invalid username or password" in str(exc_info.value)


# Profile Tests
def test_get_user_profile_success(app, test_user):
    """Test successful user profile retrieval."""
    with app.app_context():
        response = UserService.get_user_profile(test_user.id)

        assert response.username == test_user.username
        assert response.email == test_user.email
        assert response.id == test_user.id


def test_get_user_profile_not_found(app):
    """Test user profile retrieval with invalid ID."""
    with app.app_context():
        with pytest.raises(NotFoundException) as exc_info:
            UserService.get_user_profile("invalid-user-id")

        assert "User not found" in str(exc_info.value)
