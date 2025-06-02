from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.schema.user import UserResponse


class CommentCreateRequest(BaseModel):
    content: str = Field(min_length=3, max_length=200, description="Comment content")
    message_id: str = Field(description="Message ID")
    parent_id: str | None = Field(None, description="Parent comment ID for replies")

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate comment content."""
        if not v.strip():
            raise ValueError("Comment content cannot be empty")
        return v.strip()


class CommentUpdateRequest(BaseModel):
    content: str = Field(min_length=3, max_length=200, description="Comment content")

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate comment content."""
        if not v.strip():
            raise ValueError("Comment content cannot be empty")
        return v.strip()


class CommentResponse(BaseModel):
    id: str = Field(description="Comment ID")
    content: str = Field(description="Comment content")
    message_id: str = Field(description="Message ID")
    author: UserResponse = Field(description="Author")
    parent_id: str | None = Field(None, description="Parent comment ID")
    replies: list["CommentResponse"] = Field(default=[], description="Nested replies")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")

    @classmethod
    def from_model(
        cls, comment, user, replies: list["CommentResponse"] | None = None
    ) -> "CommentResponse":
        """Create CommentResponse from Comment model."""
        return cls(
            id=comment.id,
            content=comment.content,
            message_id=comment.message_id,
            author=UserResponse.from_model(user),
            parent_id=comment.parent_id,
            replies=replies or [],
            created_at=comment.created_at,
            updated_at=comment.updated_at,
        )

    model_config = {"from_attributes": True}
