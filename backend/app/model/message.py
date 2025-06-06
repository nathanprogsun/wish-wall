import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
)

from app.common.database import Base


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