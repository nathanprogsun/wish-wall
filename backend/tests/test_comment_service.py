"""
Test suite for CommentService functionality using function style.
"""

import pytest

from app.common.exception import (
    ForbiddenException,
    NotFoundException,
)
from app.schema.comment import (
    CommentCreateRequest,
    CommentUpdateRequest,
)
from app.service.comment_service import CommentService


def test_create_comment_success(db_session, test_user, test_message):
    """Test successful comment creation."""
    request = CommentCreateRequest(
        content="This is a great message!", message_id=test_message.id
    )

    response = CommentService.create_comment(test_user.id, request)

    assert response.content == "This is a great message!"
    assert response.message_id == test_message.id
    assert response.author.id == test_user.id
    assert response.parent_id is None


def test_create_reply_success(db_session, test_user, test_message, test_comment):
    """Test successful reply creation."""
    request = CommentCreateRequest(
        content="This is a reply!",
        message_id=test_message.id,
        parent_id=test_comment.id,
    )

    response = CommentService.create_comment(test_user.id, request)

    assert response.content == "This is a reply!"
    assert response.parent_id == test_comment.id


def test_create_comment_user_not_found(db_session, test_message):
    """Test comment creation with invalid user ID."""
    request = CommentCreateRequest(
        content="This is a test comment.", message_id=test_message.id
    )

    with pytest.raises(NotFoundException) as exc_info:
        CommentService.create_comment("invalid-user-id", request)

    assert "User not found" in str(exc_info.value)


def test_create_comment_message_not_found(db_session, test_user):
    """Test comment creation with invalid message ID."""
    request = CommentCreateRequest(
        content="This is a test comment.", message_id="invalid-message-id"
    )

    with pytest.raises(NotFoundException) as exc_info:
        CommentService.create_comment(test_user.id, request)

    assert "Message not found" in str(exc_info.value)


def test_update_comment_success(db_session, test_comment, test_user):
    """Test successful comment update."""
    request = CommentUpdateRequest(content="Updated comment content")

    response = CommentService.update_comment(test_comment.id, test_user.id, request)

    assert response.content == "Updated comment content"
    assert response.id == test_comment.id


def test_update_comment_not_found(db_session, test_user):
    """Test comment update with invalid comment ID."""
    request = CommentUpdateRequest(content="Updated content")

    with pytest.raises(NotFoundException) as exc_info:
        CommentService.update_comment("invalid-comment-id", test_user.id, request)

    assert "Comment not found" in str(exc_info.value)


def test_update_comment_forbidden(db_session, test_comment, second_user):
    """Test comment update by non-author."""
    request = CommentUpdateRequest(content="Updated content")

    with pytest.raises(ForbiddenException) as exc_info:
        CommentService.update_comment(test_comment.id, second_user.id, request)

    assert "Only comment author can edit" in str(exc_info.value)


def test_delete_comment_success(db_session, test_comment, test_user):
    """Test successful comment deletion."""
    CommentService.delete_comment(test_comment.id, test_user.id)

    # Comment should be soft deleted
    assert test_comment.deleted_at is not None


def test_delete_comment_not_found(db_session, test_user):
    """Test comment deletion with invalid comment ID."""
    with pytest.raises(NotFoundException) as exc_info:
        CommentService.delete_comment("invalid-comment-id", test_user.id)

    assert "Comment not found" in str(exc_info.value)


def test_delete_comment_forbidden(db_session, test_comment, second_user):
    """Test comment deletion by non-author."""
    with pytest.raises(ForbiddenException) as exc_info:
        CommentService.delete_comment(test_comment.id, second_user.id)

    assert "Only comment author can delete" in str(exc_info.value)
