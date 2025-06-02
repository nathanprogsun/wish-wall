from datetime import UTC, datetime

from app.common.database import get_db_session
from app.common.exception import (
    ForbiddenException,
    NotFoundException,
)
from app.model.comment import Comment
from app.model.message import Message
from app.model.user import User
from app.schema.comment import (
    CommentCreateRequest,
    CommentResponse,
    CommentUpdateRequest,
)


class CommentService:
    @staticmethod
    def create_comment(user_id: str, request: CommentCreateRequest) -> CommentResponse:
        db_session = get_db_session()

        # Verify user exists
        user = db_session.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundException("User not found")

        # Verify message exists and is published
        message = (
            db_session.query(Message).filter(Message.id == request.message_id).first()
        )
        if not message:
            raise NotFoundException("Message not found")

        # Verify parent comment exists if specified
        parent_comment = None
        if request.parent_id:
            parent_comment = (
                db_session.query(Comment)
                .filter(Comment.id == request.parent_id)
                .first()
            )
            if not parent_comment or parent_comment.message_id != request.message_id:
                raise NotFoundException("Parent comment not found")

        # Create comment
        comment = Comment.create_comment(
            content=request.content,
            message_id=request.message_id,
            parent_id=request.parent_id,
            author_id=user_id,
        )

        return CommentResponse(
            id=comment.id,
            content=comment.content,
            message_id=comment.message_id,
            author=user,
            parent_id=comment.parent_id,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
        )

    @staticmethod
    def update_comment(
        comment_id: str, user_id: str, request: CommentUpdateRequest
    ) -> CommentResponse:
        db_session = get_db_session()
        comment = db_session.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise NotFoundException("Comment not found")

        # Check if user is the author
        if comment.author_id != user_id:
            raise ForbiddenException("Only comment author can edit")

        user = db_session.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundException("User not found")

        comment.content = request.content
        comment.updated_at = datetime.now(UTC)
        db_session.commit()

        return CommentResponse(
            id=comment.id,
            content=comment.content,
            message_id=comment.message_id,
            author=user,
            parent_id=comment.parent_id,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
        )

    @staticmethod
    def delete_comment(comment_id: str, user_id: str) -> None:
        db_session = get_db_session()
        comment = db_session.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise NotFoundException("Comment not found")

        # Check if user is the author
        if comment.author_id != user_id:
            raise ForbiddenException("Only comment author can delete")

        # Soft delete the comment
        comment.deleted_at = datetime.now(UTC)
        comment.updated_at = datetime.now(UTC)
        db_session.commit()
