from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.model.user import User


class UserRegisterRequest(BaseModel):
    username: str = Field(min_length=5, max_length=20, description="Username")
    email: EmailStr = Field(description="Email address")
    password: str = Field(min_length=8, max_length=20, description="Password")

    model_config = {"str_strip_whitespace": True}

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format and uniqueness."""
        # Check length (5-20)
        if not 5 <= len(v) <= 20:
            raise ValueError("Username must be between 5 and 20 characters")

        # Only allow letters and numbers (no underscores)
        if not v.isalnum():
            raise ValueError("Username can only contain letters and numbers")

        # Check uniqueness
        if User.find_by_username(v):
            raise ValueError("Username already exists")
        return v.strip()

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: EmailStr) -> EmailStr:
        """Validate email uniqueness."""
        if User.find_by_email(str(v)):
            raise ValueError("Email already exists")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password complexity according to requirements."""
        # Check length (8-20)
        if not 8 <= len(v) <= 20:
            raise ValueError("Password must be between 8 and 20 characters")

        # Check for at least one uppercase letter
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")

        # Check for at least one lowercase letter
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")

        # Check for at least one digit
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")

        # Check for at least one special character
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in v):
            raise ValueError("Password must contain at least one special character")

        return v


class UserLoginRequest(BaseModel):
    login: str = Field(min_length=1, description="Username or email")
    password: str = Field(description="Password")
    remember_me: bool = Field(default=False, description="Remember me option")

    @field_validator("login")
    @classmethod
    def validate_login(cls, v: str) -> str:
        """Validate login field."""
        return v.strip()


class UserResponse(BaseModel):
    id: str = Field(description="User ID")
    username: str = Field(description="Username")
    email: str = Field(description="Email address")
    created_at: datetime = Field(description="Account creation time")
    updated_at: datetime = Field(description="Last update time")

    @classmethod
    def from_model(cls, user: User) -> "UserResponse":
        """Create UserResponse from User model."""
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    model_config = {"from_attributes": True}
