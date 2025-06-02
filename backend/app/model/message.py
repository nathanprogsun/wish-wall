import uuid
from datetime import UTC, datetime
from typing import Any, Optional

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.common.database import Base, get_db_session
from app.model.comment import Comment


class Message(Base):
    __tablename__ = "message"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    content = Column(Text, nullable=False)
    author_id = Column(String(36), ForeignKey("user.id"), nullable=False)

    created_at = Column(
        DateTime, default=lambda: datetime.now(UTC), nullable=False, index=True
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    def __init__(
        self,
        content: str,
        author_id: str,
        id: str | None = None,
    ) -> None:
        """Initialize Message instance."""
        self.id = id or str(uuid.uuid4())
        self.content = content
        self.author_id = author_id

    def __repr__(self) -> str:
        """String representation of Message."""
        return f"<Message {self.content[:50]}...>"

    def get_comment_count(self) -> int:
        db_session = get_db_session()
        return db_session.query(Comment).filter(Comment.message_id == self.id).count()

    @classmethod
    def create_message(
        cls,
        content: str,
        author_id: str,
    ) -> "Message":
        db_session = get_db_session()
        message = cls(
            content=content,
            author_id=author_id,
        )

        db_session.add(message)
        db_session.commit()
        return message

    @staticmethod
    def find_by_id(message_id: str) -> Optional["Message"]:
        """Find message by ID."""
        db_session = get_db_session()
        return db_session.query(Message).filter(Message.id == message_id).first()
