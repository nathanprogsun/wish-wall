import os
from datetime import timedelta
from pathlib import Path
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict
from yarl import URL


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    base_dir: str = os.path.dirname(os.path.abspath(__file__))

    # Flask configuration
    debug: bool = True
    secret_key: str = "your-secret-key-here"
    testing: bool = False

    # Database configuration
    database_url: str = ""
    db_path: str = os.environ.get(
        "DATABASE_PATH", os.path.join(base_dir, "data", "backend.db")
    )

    # Session configuration
    session_type: str = "filesystem"
    session_file_dir: str = os.path.join(base_dir, "data", "sessions")
    session_file_threshold: int = 500
    session_file_mode: int = 0o600
    permanent_session_lifetime: timedelta = timedelta(
        days=int(os.environ.get("SESSION_LIFETIME_DAYS", "30"))
    )

    # Session cookie configuration
    session_cookie_name: str = "session"
    session_cookie_domain: str | None = None
    session_cookie_path: str = "/"
    session_cookie_httponly: bool = True
    session_cookie_secure: bool = False  # 开发环境设为False，生产环境应设为True
    session_cookie_samesite: str = "Lax"  # 重要：设置SameSite策略
    session_refresh_each_request: bool = True

    # Remember me configuration
    remember_cookie_name: str = "remember_token"
    remember_cookie_duration: timedelta = timedelta(
        days=int(os.environ.get("REMEMBER_COOKIE_DAYS", "30"))
    )
    remember_cookie_secure: bool = False
    remember_cookie_httponly: bool = True
    remember_cookie_samesite: str = "Lax"  # 添加SameSite设置
    remember_cookie_domain: str | None = None  # 不硬编码域名

    # CORS
    allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ]

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100

    # Comment settings
    max_comment_depth: int = 5
    max_comment_length: int = 10000

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/app.log"

    # API Configuration
    api_prefix: str = "/api"
    api_version: str = "v1"

    # File paths
    data_dir: str = "data"
    logs_dir: str = "logs"

    # Swagger documentation
    swagger_ui_enabled: bool = True

    @property
    def db_url(self) -> str:
        """Get database URL for backwards compatibility."""
        return self.database_url

    @property
    def cors_origins_list(self) -> list[str]:
        """Get CORS origins as list."""
        return self.allowed_origins

    def to_flask_config(self) -> dict[str, Any]:
        """Convert settings to Flask configuration format."""
        return {
            "SECRET_KEY": self.secret_key,
            "DEBUG": self.debug,
            "TESTING": self.testing,
            "SESSION_TYPE": self.session_type,
            "SESSION_FILE_DIR": self.session_file_dir,
            "SESSION_FILE_THRESHOLD": self.session_file_threshold,
            "SESSION_FILE_MODE": self.session_file_mode,
            "PERMANENT_SESSION_LIFETIME": self.permanent_session_lifetime,
            # Session cookie settings
            "SESSION_COOKIE_NAME": self.session_cookie_name,
            "SESSION_COOKIE_DOMAIN": self.session_cookie_domain,
            "SESSION_COOKIE_PATH": self.session_cookie_path,
            "SESSION_COOKIE_HTTPONLY": self.session_cookie_httponly,
            "SESSION_COOKIE_SECURE": self.session_cookie_secure,
            "SESSION_COOKIE_SAMESITE": self.session_cookie_samesite,
            "SESSION_REFRESH_EACH_REQUEST": self.session_refresh_each_request,
            # Remember me cookie settings
            "REMEMBER_COOKIE_NAME": self.remember_cookie_name,
            "REMEMBER_COOKIE_DURATION": self.remember_cookie_duration,
            "REMEMBER_COOKIE_SECURE": self.remember_cookie_secure,
            "REMEMBER_COOKIE_HTTPONLY": self.remember_cookie_httponly,
            "REMEMBER_COOKIE_SAMESITE": self.remember_cookie_samesite,
            "REMEMBER_COOKIE_DOMAIN": self.remember_cookie_domain,
        }

    def get_database_url(self) -> str:
        """Assemble the database URL."""
        db_path_obj = Path(self.db_path)
        if not db_path_obj.is_absolute():
            db_path_obj = db_path_obj.resolve()
        # Use proper SQLite URL format with three slashes
        return str(URL(f"sqlite:///{db_path_obj}"))

    def __init__(self, **kwargs) -> None:
        """Initialize settings."""
        super().__init__(**kwargs)
        if not self.database_url:
            self.database_url = self.get_database_url()


# Global settings instance
settings = Settings()
