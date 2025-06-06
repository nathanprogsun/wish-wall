import uuid
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Text

from app.common.database import Base


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