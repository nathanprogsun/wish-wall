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
    # Access attributes before the session context to avoid detached instance
    message_id = test_message.id
    user_id = test_user.id
    
    request = CommentCreateRequest(
        content="This is a great message!", message_id=message_id
    )

    response = CommentService.create_comment(user_id, request)

    assert response.content == "This is a great message!"
    assert response.message_id == message_id
    assert response.author.id == user_id
    assert response.parent_id is None


def test_create_reply_success(db_session, test_user, test_message, test_comment):
    """Test successful reply creation."""
    # Access attributes before the session context to avoid detached instance
    message_id = test_message.id
    comment_id = test_comment.id
    user_id = test_user.id
    
    request = CommentCreateRequest(
        content="This is a reply!",
        message_id=message_id,
        parent_id=comment_id,
    )

    response = CommentService.create_comment(user_id, request)

    assert response.content == "This is a reply!"
    assert response.parent_id == comment_id


def test_create_comment_user_not_found(db_session, test_message):
    """Test comment creation with invalid user ID."""
    # Access attributes before the session context to avoid detached instance
    message_id = test_message.id
    
    request = CommentCreateRequest(
        content="This is a test comment.", message_id=message_id
    )

    with pytest.raises(NotFoundException) as exc_info:
        CommentService.create_comment("invalid-user-id", request)

    assert "User not found" in str(exc_info.value)


def test_create_comment_message_not_found(db_session, test_user):
    """Test comment creation with invalid message ID."""
    # Access attributes before the session context to avoid detached instance
    user_id = test_user.id
    
    request = CommentCreateRequest(
        content="This is a test comment.", message_id="invalid-message-id"
    )

    with pytest.raises(NotFoundException) as exc_info:
        CommentService.create_comment(user_id, request)

    assert "Message not found" in str(exc_info.value)


def test_update_comment_success(db_session, test_comment, test_user):
    """Test successful comment update."""
    # Access attributes before the session context to avoid detached instance
    comment_id = test_comment.id
    user_id = test_user.id
    
    request = CommentUpdateRequest(content="Updated comment content")

    response = CommentService.update_comment(comment_id, user_id, request)

    assert response.content == "Updated comment content"
    assert response.id == comment_id


def test_update_comment_not_found(db_session, test_user):
    """Test comment update with invalid comment ID."""
    # Access attributes before the session context to avoid detached instance
    user_id = test_user.id
    
    request = CommentUpdateRequest(content="Updated content")

    with pytest.raises(NotFoundException) as exc_info:
        CommentService.update_comment("invalid-comment-id", user_id, request)

    assert "Comment not found" in str(exc_info.value)


def test_update_comment_forbidden(db_session, test_comment, second_user):
    """Test comment update by non-author."""
    # Access attributes before the session context to avoid detached instance
    comment_id = test_comment.id
    user_id = second_user.id
    
    request = CommentUpdateRequest(content="Updated content")

    with pytest.raises(ForbiddenException) as exc_info:
        CommentService.update_comment(comment_id, user_id, request)

    assert "Only comment author can edit" in str(exc_info.value)


def test_delete_comment_success(db_session, test_comment, test_user):
    """Test successful comment deletion."""
    # Access attributes before the session context to avoid detached instance
    comment_id = test_comment.id
    user_id = test_user.id
    
    CommentService.delete_comment(comment_id, user_id)

    # Reload comment from database to check deletion
    from app.common.database import get_db_session
    from app.model.comment import Comment
    
    with get_db_session() as session:
        updated_comment = session.query(Comment).filter(Comment.id == comment_id).first()
        assert updated_comment.deleted_at is not None


def test_delete_comment_not_found(db_session, test_user):
    """Test comment deletion with invalid comment ID."""
    # Access attributes before the session context to avoid detached instance
    user_id = test_user.id
    
    with pytest.raises(NotFoundException) as exc_info:
        CommentService.delete_comment("invalid-comment-id", user_id)

    assert "Comment not found" in str(exc_info.value)


def test_delete_comment_forbidden(db_session, test_comment, second_user):
    """Test comment deletion by non-author."""
    # Access attributes before the session context to avoid detached instance
    comment_id = test_comment.id
    user_id = second_user.id
    
    with pytest.raises(ForbiddenException) as exc_info:
        CommentService.delete_comment(comment_id, user_id)

    assert "Only comment author can delete" in str(exc_info.value)
