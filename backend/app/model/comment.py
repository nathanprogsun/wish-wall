import uuid
from datetime import UTC, datetime
from typing import Any, Optional

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.common.database import Base, get_db_session


class Comment(Base):
    __tablename__ = "comment"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    content = Column(Text, nullable=False)

    author_id = Column(String(36), ForeignKey("user.id"), nullable=False)
    message_id = Column(String(36), ForeignKey("message.id"), nullable=False)
    parent_id = Column(String(36), ForeignKey("comment.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.now(UTC), nullable=False, index=True)
    updated_at = Column(
        DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC), nullable=False
    )
    deleted_at = Column(DateTime, nullable=True)

    def __init__(
        self,
        content: str,
        author_id: str,
        message_id: str,
        parent_id: str | None = None,
        id: str | None = None,
    ) -> None:
        """Initialize Comment instance."""
        self.id = id or str(uuid.uuid4())
        self.content = content
        self.author_id = author_id
        self.message_id = message_id
        self.parent_id = parent_id

    def __repr__(self) -> str:
        """String representation of Comment."""
        return f"<Comment {self.id}: {self.content[:50]}...>"

    @classmethod
    def create_comment(
        cls, content: str, author_id: str, message_id: str, parent_id: str | None = None
    ) -> "Comment":
        """Create a new comment."""
        db_session = get_db_session()
        comment = cls(
            content=content,
            message_id=message_id,
            parent_id=parent_id,
            author_id=author_id,
        )

        db_session.add(comment)
        db_session.flush()  # Get the ID
        db_session.commit()
        return comment

    @staticmethod
    def find_by_id(comment_id: str) -> Optional["Comment"]:
        """Find comment by ID."""
        db_session = get_db_session()
        return db_session.query(Comment).filter(Comment.id == comment_id).first()

    @staticmethod
    def find_all_by_message_id(
        message_id: str,
        parent_id: str | None = None,
    ) -> list["Comment"]:
        """Get comments for a specific message."""
        db_session = get_db_session()
        query = db_session.query(Comment).filter(
            Comment.message_id == message_id,
            Comment.deleted_at.is_(None),
        )

        if parent_id:
            query = query.filter(Comment.parent_id == parent_id)
        else:
            query = query.filter(Comment.parent_id.is_(None))

        query = query.order_by(Comment.created_at.desc())
        return query.all()

    @staticmethod
    def find_all_comments_by_message_id(message_id: str) -> list["Comment"]:
        """Get ALL comments for a specific message (including nested ones)."""
        db_session = get_db_session()
        query = db_session.query(Comment).filter(
            Comment.message_id == message_id,
            Comment.deleted_at.is_(None),
        )
        return query.all()
