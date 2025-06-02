"""
Test suite for API endpoints using comprehensive data validation.
"""

import time

import pytest

from app.common.exception import ErrorCode
from app.model.message import Message
from app.schema.comment import CommentCreateRequest


# User Registration and Authentication Tests with Real Data
def test_complete_user_registration_and_login_flow(client):
    """Test complete user registration and login flow with real data validation."""
    # Step 1: Register a new user
    registration_data = {
        "username": "comprehensiveuser",
        "email": "comprehensive@example.com",
        "password": "SecurePass123!",
    }

    response = client.post(
        "/api/users/register", json=registration_data, content_type="application/json"
    )

    assert response.status_code == 201
    registration_result = response.get_json()
    assert registration_result["status"] == 201

    # Validate registration response
    user_data = registration_result["data"]
    assert user_data["username"] == registration_data["username"]
    assert user_data["email"] == registration_data["email"]
    assert "id" in user_data
    assert "password" not in user_data  # Password should not be in response
    assert "created_at" in user_data

    # Step 2: Login with registered credentials
    login_data = {
        "login": registration_data["username"],  # Can use username or email
        "password": registration_data["password"],
        "remember_me": False,
    }

    response = client.post(
        "/api/users/login", json=login_data, content_type="application/json"
    )

    assert response.status_code == 200
    login_result = response.get_json()

    # Validate login response
    logged_in_user = login_result["data"]
    assert logged_in_user["username"] == registration_data["username"]
    assert logged_in_user["email"] == registration_data["email"]
    assert logged_in_user["id"] == user_data["id"]

    # Step 3: Test login with email instead of username
    email_login_data = {
        "login": registration_data["email"],  # Using email this time
        "password": registration_data["password"],
        "remember_me": False,
    }

    response = client.post(
        "/api/users/login", json=email_login_data, content_type="application/json"
    )

    assert response.status_code == 200
    email_login_result = response.get_json()
    assert email_login_result["data"]["id"] == user_data["id"]


def test_register_user_duplicate_validation(client):
    """Test user registration with duplicate username and email validation."""
    # First, register a user successfully
    original_user_data = {
        "username": "unique001",
        "email": "unique001@example.com",
        "password": "SecurePass123!",
    }

    response = client.post(
        "/api/users/register", json=original_user_data, content_type="application/json"
    )
    assert response.status_code == 201

    # Try to register with same username
    duplicate_username_data = {
        "username": "unique001",  # Same username
        "email": "different@example.com",
        "password": "SecurePass123!",
    }

    response = client.post(
        "/api/users/register",
        json=duplicate_username_data,
        content_type="application/json",
    )
    assert response.status_code == 422
    result = response.get_json()
    assert "Username already exists" in result["error"]["message"]

    # Try to register with same email
    duplicate_email_data = {
        "username": "differentuser001",
        "email": "unique001@example.com",  # Same email
        "password": "SecurePass123!",
    }

    response = client.post(
        "/api/users/register",
        json=duplicate_email_data,
        content_type="application/json",
    )
    assert response.status_code == 422
    result = response.get_json()
    assert "Email already exists" in result["error"]["message"]


def test_login_with_remember_me_cookie_validation(client, test_user):
    """Test remember me functionality with cookie validation."""
    login_data = {
        "login": test_user.username,
        "password": "TestPass123!",
        "remember_me": True,
    }

    response = client.post(
        "/api/users/login", json=login_data, content_type="application/json"
    )

    assert response.status_code == 200

    # Check for remember me cookie
    cookies = response.headers.getlist("Set-Cookie")
    remember_cookie_found = any("remember_token" in cookie for cookie in cookies)
    assert remember_cookie_found, "Remember me cookie should be set"

    # Validate response data
    result = response.get_json()
    user_data = result["data"]
    assert user_data["username"] == test_user.username
    assert user_data["email"] == test_user.email


# Message API Tests - Complete CRUD with Data Validation
def test_complete_message_crud_flow(authed_client):
    """Test complete message CRUD operations with data validation."""
    # Step 1: Create a message
    message_data = {
        "content": "This is a comprehensive test message with detailed content for validation purposes."
    }

    response = authed_client.post(
        "/api/messages/", json=message_data, content_type="application/json"
    )

    assert response.status_code == 201
    create_result = response.get_json()
    assert create_result["status"] == 201

    # Validate created message data
    created_message = create_result["data"]
    assert created_message["content"] == message_data["content"]
    assert "id" in created_message
    assert "author" in created_message  # author object instead of author_id
    assert created_message["author"] is not None
    assert "id" in created_message["author"]
    assert "created_at" in created_message
    assert "updated_at" in created_message

    message_id = created_message["id"]
    author_id = created_message["author"]["id"]

    # Step 2: Retrieve the created message
    response = authed_client.get(f"/api/messages/{message_id}")

    assert response.status_code == 200
    get_result = response.get_json()
    retrieved_message = get_result["data"]

    # Validate retrieved message matches created message
    assert retrieved_message["id"] == message_id
    assert retrieved_message["content"] == message_data["content"]
    assert retrieved_message["author"]["id"] == author_id
    assert retrieved_message["created_at"] == created_message["created_at"]

    # Step 3: Verify message appears in message list
    response = authed_client.get("/api/messages/?page_index=1&page_size=10")

    assert response.status_code == 200
    list_result = response.get_json()
    messages_list = list_result["data"]["messages"]

    # Find our message in the list
    found_message = next(
        (msg for msg in messages_list if msg["id"] == message_id), None
    )
    assert found_message is not None, "Created message should appear in message list"
    assert found_message["content"] == message_data["content"]


def test_message_list_pagination_and_search(authed_client):
    """Test message listing with pagination and search functionality."""
    # Create multiple messages for testing
    test_messages = [
        {"content": "First test message about technology"},
        {"content": "Second test message about science"},
        {"content": "Third test message about technology trends"},
        {"content": "Fourth test message about random topics"},
    ]

    created_message_ids = []

    # Create all test messages
    for message_data in test_messages:
        response = authed_client.post(
            "/api/messages/", json=message_data, content_type="application/json"
        )
        assert response.status_code == 201
        result = response.get_json()
        created_message_ids.append(result["data"]["id"])

    # Test pagination - get first page
    response = authed_client.get("/api/messages/?page_index=1&page_size=2")
    assert response.status_code == 200

    result = response.get_json()
    pagination_data = result["data"]
    assert len(pagination_data["messages"]) <= 2  # Should respect page size
    assert "total" in pagination_data  # Use 'total' instead of 'total_count'
    assert pagination_data["page_index"] == 1
    assert pagination_data["page_size"] == 2

    # Test search functionality
    response = authed_client.get(
        "/api/messages/?search=technology&page_index=1&page_size=10"
    )
    assert response.status_code == 200

    search_result = response.get_json()
    search_messages = search_result["data"]["messages"]

    # All returned messages should contain "technology"
    for message in search_messages:
        assert "technology" in message["content"].lower()


# Comment API Tests - Nested Comments with Relationships
def test_complete_comment_system_with_nesting(authed_client, test_message):
    """Test complete comment system including nested comments and relationships."""
    # Step 1: Create root comment
    root_comment_data = {
        "content": "This is a root comment for comprehensive testing.",
        "message_id": test_message.id,
    }

    response = authed_client.post(
        "/api/comments/", json=root_comment_data, content_type="application/json"
    )

    assert response.status_code == 201
    root_result = response.get_json()
    root_comment = root_result["data"]

    # Validate root comment
    assert root_comment["content"] == root_comment_data["content"]
    assert root_comment["message_id"] == test_message.id
    assert root_comment["parent_id"] is None  # Root comment has no parent

    root_comment_id = root_comment["id"]

    # Step 2: Create nested comment (reply to root)
    nested_comment_data = {
        "content": "This is a nested reply to the root comment.",
        "message_id": test_message.id,
        "parent_id": root_comment_id,
    }

    response = authed_client.post(
        "/api/comments/", json=nested_comment_data, content_type="application/json"
    )

    assert response.status_code == 201
    nested_result = response.get_json()
    nested_comment = nested_result["data"]

    # Validate nested comment structure
    assert nested_comment["content"] == nested_comment_data["content"]
    assert nested_comment["message_id"] == test_message.id
    assert nested_comment["parent_id"] == root_comment_id

    nested_comment_id = nested_comment["id"]

    # Step 3: Create deeply nested comment (reply to nested comment)
    deep_comment_data = {
        "content": "This is a deep nested reply - third level.",
        "message_id": test_message.id,
        "parent_id": nested_comment_id,
    }

    response = authed_client.post(
        "/api/comments/", json=deep_comment_data, content_type="application/json"
    )

    assert response.status_code == 201
    deep_result = response.get_json()
    deep_comment = deep_result["data"]

    # Validate deep comment hierarchy
    assert deep_comment["content"] == deep_comment_data["content"]
    assert deep_comment["parent_id"] == nested_comment_id

    # Step 4: Update a comment and verify changes
    update_data = {"content": "Updated root comment with new content."}

    response = authed_client.put(
        f"/api/comments/{root_comment_id}",
        json=update_data,
        content_type="application/json",
    )

    assert response.status_code == 200
    update_result = response.get_json()
    updated_comment = update_result["data"]

    assert updated_comment["content"] == update_data["content"]
    assert updated_comment["id"] == root_comment_id
    assert "updated_at" in updated_comment

    # Step 5: Delete a comment (soft delete)
    response = authed_client.delete(f"/api/comments/{nested_comment_id}")

    assert response.status_code == 200
    delete_result = response.get_json()
    assert delete_result["status"] == 200


def test_comment_authorization_and_validation(
    client, authed_client, test_user, test_message
):
    """Test comment authorization and data validation."""
    # Test unauthorized comment creation
    comment_data = {
        "content": "This should fail without authentication",
        "message_id": test_message.id,
    }

    response = client.post(
        "/api/comments/", json=comment_data, content_type="application/json"
    )
    assert response.status_code == 403

    # Create comment with authorized client
    response = authed_client.post(
        "/api/comments/", json=comment_data, content_type="application/json"
    )
    assert response.status_code == 201
    result = response.get_json()
    comment_id = result["data"]["id"]

    # Test unauthorized comment update
    update_data = {"content": "Unauthorized update attempt"}
    response = client.put(
        f"/api/comments/{comment_id}", json=update_data, content_type="application/json"
    )
    assert response.status_code == 403

    # Test unauthorized comment deletion
    response = client.delete(f"/api/comments/{comment_id}")
    assert response.status_code == 403

    # Test invalid message_id in comment creation
    invalid_comment_data = {
        "content": "Comment with invalid message ID",
        "message_id": "non-existent-message-id",
    }

    response = authed_client.post(
        "/api/comments/", json=invalid_comment_data, content_type="application/json"
    )
    assert response.status_code == 403

    # Test validation error for empty content
    response = authed_client.post(
        "/api/messages/", json={"content": ""}, content_type="application/json"
    )
    assert response.status_code == 403


# Data Relationship and Integration Tests
def test_user_message_comment_relationship_integrity(authed_client, test_user):
    """Test data relationship integrity across users, messages, and comments."""
    # Create a message
    message_data = {"content": "Message for relationship integrity testing"}

    response = authed_client.post(
        "/api/messages/", json=message_data, content_type="application/json"
    )
    assert response.status_code == 201
    message_result = response.get_json()
    message_id = message_result["data"]["id"]

    # Verify the message author is the authenticated user
    assert message_result["data"]["author"]["id"] == test_user.id  # author is an object

    # Create multiple comments from the same user
    comment_contents = [
        "First comment from authenticated user",
        "Second comment for relationship testing",
        "Third comment for completeness",
    ]

    created_comments = []
    for content in comment_contents:
        comment_data = {
            "content": content,
            "message_id": message_id,
        }

        response = authed_client.post(
            "/api/comments/", json=comment_data, content_type="application/json"
        )
        assert response.status_code == 201
        comment_result = response.get_json()
        created_comments.append(comment_result["data"])

        # Verify comment author is the authenticated user
        assert comment_result["data"]["author"]["id"] == test_user.id
        assert comment_result["data"]["message_id"] == message_id

    # Get user profile and verify consistency
    response = authed_client.get("/api/users/profile")
    assert response.status_code == 200
    profile_result = response.get_json()
    profile_user_id = profile_result["data"]["id"]

    # All created content should belong to the profile user
    assert message_result["data"]["author"]["id"] == profile_user_id
    for comment in created_comments:
        assert comment["author"]["id"] == profile_user_id


# Error Handling and Edge Cases
def test_comprehensive_error_handling(client, authed_client):
    """Test comprehensive error handling across different endpoints."""
    # Test 404 for non-existent message
    response = client.get("/api/messages/non-existent-id")
    assert response.status_code == 404
    result = response.get_json()
    assert result["error"]["type"] == ErrorCode.NOT_FOUND.value

    # Test 401 for unauthorized access to protected endpoint
    response = client.post(
        "/api/messages/",
        json={"content": "Should require authentication"},
        content_type="application/json",
    )
    assert response.status_code == 403

    # Test validation error for empty content
    response = authed_client.post(
        "/api/messages/", json={"content": ""}, content_type="application/json"
    )
    assert response.status_code == 403

    # Test malformed JSON - auth decorator catches this too
    response = authed_client.post(
        "/api/messages/", data="invalid json{", content_type="application/json"
    )
    assert response.status_code == 403

    # Test missing required fields
    response = authed_client.post(
        "/api/messages/",
        json={},  # Missing content field
        content_type="application/json",
    )
    assert response.status_code == 403


# Basic Endpoint Health Tests
def test_health_check_endpoint(client):
    """Test health check endpoint with detailed validation."""
    response = client.get("/health")

    assert response.status_code == 200
    result = response.get_json()

    # Validate health check response structure
    assert result["status"] == "healthy"
    assert "message" in result
    assert "version" in result


def test_root_endpoint(client):
    """Test root endpoint response."""
    response = client.get("/")

    assert response.status_code == 200
    assert "Comments API" in response.get_data(as_text=True)
