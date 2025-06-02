import uuid
from datetime import UTC, datetime
from typing import Any, Optional

from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from app.common.database import Base, get_db_session


class User(Base):
    __tablename__ = "user"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    created_at = Column(DateTime, default=datetime.now(UTC), nullable=False)
    updated_at = Column(
        DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC), nullable=False
    )
    last_login_at = Column(DateTime, nullable=True)

    def __init__(
        self,
        username: str,
        email: str,
        password: str,
        id: str | None = None,
    ) -> None:
        """Initialize User instance."""
        self.id = id or str(uuid.uuid4())
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)

    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User {self.username}>"

    def set_password(self, password: str) -> None:
        """Set user password hash."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check if provided password matches hash."""
        return check_password_hash(self.password_hash, password)

    def update_last_login(self) -> None:
        """Update last login timestamp."""
        self.last_login_at = datetime.now(UTC)

    @classmethod
    def create_user(
        cls,
        username: str,
        email: str,
        password: str,
    ) -> "User":
        db_session = get_db_session()
        user = cls(
            username=username,
            email=email,
            password=password,
        )

        db_session.add(user)
        db_session.commit()
        return user

    @staticmethod
    def find_by_id(user_id: str) -> Optional["User"]:
        db_session = get_db_session()
        return db_session.query(User).filter(User.id == user_id).first()

    @staticmethod
    def find_by_username(username: str) -> Optional["User"]:
        db_session = get_db_session()
        return db_session.query(User).filter(User.username == username).first()

    @staticmethod
    def find_by_email(email: str) -> Optional["User"]:
        db_session = get_db_session()
        return db_session.query(User).filter(User.email == email).first()

    @staticmethod
    def find_by_login(login: str) -> Optional["User"]:
        db_session = get_db_session()
        return (
            db_session.query(User)
            .filter((User.username == login) | (User.email == login))
            .first()
        )
