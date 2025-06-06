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
    reset_database_connection,
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
def app():
    """
    Create Flask application for testing.

    Returns:
        Flask application configured for testing
    """
    # Override environment variables for testing
    os.environ["TESTING"] = "true"
    os.environ["TEST_DB_HOST"] = "localhost"
    os.environ["TEST_DB_PORT"] = "3307"
    os.environ["TEST_DB_USERNAME"] = "root"
    os.environ["TEST_DB_PASSWORD"] = "Wish_wall@2025"
    os.environ["TEST_DB_NAME"] = "wish_wall_test"
    os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
    os.environ["JWT_SECRET_KEY"] = "test-jwt-secret-key-for-testing-only"
    os.environ["DEBUG"] = "False"

    # Import settings after environment override
    from app.settings import settings
    
    # Set testing mode
    settings.testing = True
    
    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        # Initialize test database
        test_db_url = settings.get_test_database_url()
        reset_database_connection()  # Clear any existing connections
        init_database(test_db_url)
        
        # Create tables
        create_tables()
        yield app
        
        # Cleanup
        try:
            drop_tables()
        except Exception as e:
            print(f"Warning: Failed to drop tables during cleanup: {e}")
        finally:
            reset_database_connection()


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
        with get_db_session() as session:
            yield session
            # Clean up all test data after each test
            # Delete in correct order to avoid foreign key constraint issues
            try:
                # First, delete comments in reverse order (children first)
                # Get all comments ordered by depth (deepest first)
                from sqlalchemy import text
                session.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
                session.query(Comment).delete()
                session.query(Message).delete() 
                session.query(User).delete()
                session.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
                session.commit()
            except Exception as e:
                print(f"Warning: Failed to clean up test data: {e}")
                session.rollback()


# Fake data generators
@pytest.fixture
def fake_user_data() -> dict[str, Any]:
    """Generate fake user data."""
    import time
    timestamp = str(int(time.time() * 1000))[-8:]  # Last 8 digits of timestamp in ms
    return {
        "username": f"user{timestamp}",
        "email": f"user{timestamp}@example.com",
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
    import time
    timestamp = str(int(time.time() * 1000))[-8:]
    fake_user_data = {
        "username": f"fakeuser{timestamp}",
        "email": f"fake{timestamp}@example.com",
        "password": "FakePass123!",
    }

    user = User(
        username=fake_user_data["username"],
        email=fake_user_data["email"],
        password=fake_user_data["password"],
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    import time
    timestamp = str(int(time.time() * 1000))[-8:]
    user_data = {
        "username": f"testuser{timestamp}",
        "email": f"test{timestamp}@example.com",
        "password": "TestPass123!",
    }

    user = User(
        username=user_data["username"],
        email=user_data["email"],
        password=user_data["password"],
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def second_user(db_session) -> User:
    """Create second test user."""
    import time

    timestamp = str(int(time.time() * 1000))[-8:]  # Millisecond timestamp for uniqueness
    user_data = {
        "username": f"seconduser{timestamp}",
        "email": f"second{timestamp}@example.com",
        "password": "TestPass123!",
    }

    user = User(
        username=user_data["username"],
        email=user_data["email"],
        password=user_data["password"],
    )
    db_session.add(user)
    db_session.commit()
    return user


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

    timestamp = str(int(time.time() * 1000))[-8:]  # Millisecond timestamp for uniqueness
    users = []
    for i in range(5):
        user_data = {
            "username": f"multiuser{timestamp}{i}",
            "email": f"multi{timestamp}{i}@example.com",
            "password": "TestPass123!",
        }

        user = User(
            username=user_data["username"],
            email=user_data["email"],
            password=user_data["password"],
        )
        db_session.add(user)
        users.append(user)

    db_session.commit()
    return users


# Message fixtures
@pytest.fixture
def test_message(db_session, test_user):
    """Create a test message."""
    message = Message(
        content="This is a test message for testing purposes.",
        author_id=test_user.id,
    )
    db_session.add(message)
    db_session.commit()
    return message


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
        message = Message(
            content=f"Test message {i + 1} from {user.username}",
            author_id=user.id,
        )
        db_session.add(message)
        messages.append(message)

    db_session.commit()
    return messages


# Comment fixtures
@pytest.fixture
def test_comment(db_session, test_user, test_message):
    """Create a test comment."""
    comment = Comment(
        content="This is a test comment",
        author_id=test_user.id,
        message_id=test_message.id,
    )
    db_session.add(comment)
    db_session.commit()
    return comment


@pytest.fixture
def test_reply(db_session, second_user, test_message, test_comment):
    """Create a test reply to comment."""
    reply = Comment(
        content="This is a test reply",
        author_id=second_user.id,
        message_id=test_message.id,
        parent_id=test_comment.id,
    )
    db_session.add(reply)
    db_session.commit()
    return reply


@pytest.fixture
def authenticated_session(app, test_user):
    """Create authenticated session for testing."""
    from app.util.jwt_utils import generate_access_token
    
    with app.app_context():
        token = generate_access_token(str(test_user.id))
        return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def authed_client(authenticated_session):
    """Create client with authentication headers."""
    def _authed_client(client):
        def authed_request(method, *args, **kwargs):
            kwargs.setdefault("headers", {}).update(authenticated_session)
            return getattr(client, method)(*args, **kwargs)
        
        # Add authenticated methods to client
        client.authed_get = lambda *args, **kwargs: authed_request("get", *args, **kwargs)
        client.authed_post = lambda *args, **kwargs: authed_request("post", *args, **kwargs)
        client.authed_put = lambda *args, **kwargs: authed_request("put", *args, **kwargs)
        client.authed_delete = lambda *args, **kwargs: authed_request("delete", *args, **kwargs)
        
        return client
    
    return _authed_client
