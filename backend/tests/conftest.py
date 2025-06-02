"""
Pytest configuration and common fixtures for testing.
"""

import os
import tempfile
import time
from typing import Any

import pytest
from faker import Faker
from werkzeug.security import generate_password_hash

from app.__main__ import create_app
from app.common.database import (
    Base,
    get_db_session,
    get_engine,
    init_database,
)
from app.model.comment import Comment
from app.model.message import Message
from app.model.user import User

# Initialize faker
fake = Faker(["en_US", "zh_CN"])
fake.seed_instance(12345)  # For consistent test data


# Helper functions
def create_tables():
    """Create all database tables."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all database tables."""
    engine = get_engine()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def temp_db():
    """Create temporary database for testing."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    yield f"sqlite:///{db_path}"
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(scope="session")
def app(temp_db):
    """
    Create Flask application for testing.

    Returns:
        Flask application configured for testing
    """
    # Override environment variables for testing
    os.environ["DB_URL"] = temp_db
    os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
    os.environ["DEBUG"] = "False"

    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        create_tables()
        yield app
        drop_tables()


@pytest.fixture(scope="function")
def client(app):
    """
    Create test client for non-authenticated requests.

    Args:
        app: Flask application fixture

    Returns:
        Flask test client
    """
    return app.test_client()


@pytest.fixture(scope="function")
def db_session(app):
    """
    Create clean database session for each test.

    Args:
        app: Flask application fixture

    Yields:
        Clean database session
    """
    with app.app_context():
        session = get_db_session()
        yield session
        # Clean up all test data after each test
        session.query(Comment).delete()
        session.query(Message).delete()
        session.query(User).delete()
        session.commit()


# Fake data generators
@pytest.fixture
def fake_user_data() -> dict[str, Any]:
    """Generate fake user data."""
    timestamp = str(int(time.time()))[-6:]  # Last 6 digits of timestamp
    return {
        "username": f"{fake.user_name().replace('_', '').replace('.', '').lower()[:10]}{timestamp}"[
            :20
        ],  # Ensure uniqueness and valid format
        "email": f"{timestamp}_{fake.email()}",  # Ensure uniqueness
        "password": "TestPass123!",
    }


@pytest.fixture
def fake_message_data() -> dict[str, Any]:
    """Generate fake message data."""
    return {
        "content": fake.text(max_nb_chars=200)[:200],  # Ensure within limit
    }


@pytest.fixture
def fake_comment_data() -> dict[str, Any]:
    """Generate fake comment data."""
    return {"content": fake.text(max_nb_chars=200)[:200]}  # Ensure within limit


# User fixtures
@pytest.fixture
def fake_user(db_session):
    """Create a fake user for testing purposes."""
    fake_user_data = {
        "username": "fakeuser",
        "email": "fake@example.com",
        "password": "FakePass123!",
    }

    return User.create_user(
        username=fake_user_data["username"],
        email=fake_user_data["email"],
        password=fake_user_data["password"],
    )


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123!",
    }

    return User.create_user(
        username=user_data["username"],
        email=user_data["email"],
        password=user_data["password"],
    )


@pytest.fixture
def second_user(db_session) -> User:
    """Create second test user."""
    import time

    timestamp = str(int(time.time()))[-6:]  # Last 6 digits of timestamp
    user_data = {
        "username": f"{fake.user_name().replace('_', '').replace('.', '').lower()[:10]}{timestamp}2"[
            :20
        ],
        "email": f"{timestamp}_2_{fake.email()}",
        "password": "TestPass123!",
    }

    return User.create_user(
        username=user_data["username"],
        email=user_data["email"],
        password=user_data["password"],
    )


@pytest.fixture
def multiple_users(db_session) -> list[User]:
    """
    Create multiple test users.

    Args:
        db_session: Database session fixture

    Returns:
        List of User instances
    """
    import time

    timestamp = str(int(time.time()))[-6:]  # Last 6 digits of timestamp
    users = []
    for i in range(5):
        user_data = {
            "username": f"{fake.user_name().replace('_', '').replace('.', '').lower()[:8]}{timestamp}{i}"[
                :20
            ],
            "email": f"{timestamp}_{i}_{fake.email()}",
            "password": "TestPass123!",
        }

        user = User.create_user(
            username=user_data["username"],
            email=user_data["email"],
            password=user_data["password"],
        )
        users.append(user)

    return users


# Message fixtures
@pytest.fixture
def test_message(db_session, test_user):
    """Create a test message."""
    return Message.create_message(
        content="This is a test message for testing purposes.",
        author_id=test_user.id,
    )


@pytest.fixture
def multiple_messages(db_session, multiple_users) -> list[Message]:
    """
    Create multiple test messages.

    Args:
        db_session: Database session fixture
        multiple_users: Multiple users fixture

    Returns:
        List of Message instances
    """
    messages = []
    for i, user in enumerate(multiple_users):
        message = Message.create_message(
            content=f"This is test message content {i + 1}",
            author_id=user.id,
        )
        messages.append(message)

    return messages


# Comment fixtures
@pytest.fixture
def test_comment(db_session, test_user, test_message):
    """Create a test comment."""
    return Comment.create_comment(
        content="This is a test comment.",
        message_id=test_message.id,
        author_id=test_user.id,
    )


@pytest.fixture
def test_reply(db_session, second_user, test_message, test_comment):
    """Create a test reply to a comment."""
    return Comment.create_comment(
        content="This is a test reply.",
        message_id=test_message.id,
        parent_id=test_comment.id,
        author_id=second_user.id,
    )


# Authentication fixtures
@pytest.fixture
def authenticated_session(app, test_user):
    """
    Create authenticated session with test user.

    Args:
        app: Flask application fixture
        test_user: Test user fixture

    Yields:
        Authenticated session context
    """
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["user_id"] = test_user.id
        yield client


@pytest.fixture
def authed_client(authenticated_session):
    """
    Create authenticated client for testing protected endpoints.

    Args:
        authenticated_session: Authenticated session fixture

    Returns:
        Authenticated Flask test client
    """
    return authenticated_session
