from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.schema.comment import CommentResponse

from .user import UserResponse


class MessageCreateRequest(BaseModel):
    content: str = Field(min_length=3, max_length=200, description="Message content")

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Message content cannot be empty")
        return v.strip()


class MessageResponse(BaseModel):
    id: str = Field(description="Message ID")
    content: str = Field(description="Message content")
    author: UserResponse = Field(description="Message author")
    comments: list[CommentResponse] = Field(default=[], description="Message comments")
    comment_count: int = Field(default=0, description="Number of comments")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")

    model_config = {"from_attributes": True}


class MessageListRequest(BaseModel):
    page_index: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=10, ge=1, le=100, description="Items per page")
    search: str | None = Field(None, description="Search in message content")

    @field_validator("search")
    @classmethod
    def validate_search(cls, v: str | None) -> str | None:
        """Validate search term."""
        if v is not None:
            v = v.strip()
            if len(v) < 2:
                raise ValueError("Search term must be at least 2 characters")
        return v


class MessageListResponse(BaseModel):
    page_index: int = Field(default=1, description="Current page")
    page_size: int = Field(default=10, description="Items per page")
    total: int = Field(default=0, description="Total number of messages")
    messages: list[MessageResponse] = Field(default=[], description="List of messages")
