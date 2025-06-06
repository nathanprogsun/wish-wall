import os
from datetime import timedelta
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

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

    # Database configuration - MySQL
    db_host: str = os.environ.get("DB_HOST", "localhost")
    db_port: int = int(os.environ.get("DB_PORT", "3306"))
    db_username: str = os.environ.get("DB_USERNAME", "root")
    db_password: str = os.environ.get("DB_PASSWORD", "password")
    db_name: str = os.environ.get("DB_NAME", "wish_wall")
    db_charset: str = os.environ.get("DB_CHARSET", "utf8mb4")
    
    # Test Database configuration - MySQL
    test_db_host: str = os.environ.get("TEST_DB_HOST", "localhost")
    test_db_port: int = int(os.environ.get("TEST_DB_PORT", "3307"))
    test_db_username: str = os.environ.get("TEST_DB_USERNAME", "root")
    test_db_password: str = os.environ.get("TEST_DB_PASSWORD", "Wish_wall@2025")
    test_db_name: str = os.environ.get("TEST_DB_NAME", "wish_wall_test")
    test_db_charset: str = os.environ.get("TEST_DB_CHARSET", "utf8mb4")
    
    # Database connection pool settings
    db_pool_size: int = int(os.environ.get("DB_POOL_SIZE", "10"))
    db_max_overflow: int = int(os.environ.get("DB_MAX_OVERFLOW", "20"))
    db_pool_timeout: int = int(os.environ.get("DB_POOL_TIMEOUT", "30"))
    db_pool_recycle: int = int(os.environ.get("DB_POOL_RECYCLE", "3600"))
    db_echo: bool = os.environ.get("DB_ECHO", "false").lower() == "true"
    
    # Legacy database_url for backwards compatibility
    database_url: str = ""

    # JWT Configuration
    jwt_secret_key: str = os.environ.get("JWT_SECRET_KEY", "your-jwt-secret-key-here")
    jwt_algorithm: str = "HS256"
    jwt_access_token_expires: timedelta = timedelta(
        hours=int(os.environ.get("JWT_ACCESS_TOKEN_HOURS", "24"))
    )
    jwt_remember_token_expires: timedelta = timedelta(
        days=int(os.environ.get("JWT_REMEMBER_TOKEN_DAYS", "30"))
    )
    jwt_refresh_token_expires: timedelta = timedelta(
        days=int(os.environ.get("JWT_REFRESH_TOKEN_DAYS", "7"))
    )

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
        """Get MySQL database URL."""
        return self.get_mysql_database_url()

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
            # JWT Configuration
            "JWT_SECRET_KEY": self.jwt_secret_key,
            "JWT_ALGORITHM": self.jwt_algorithm,
            "JWT_ACCESS_TOKEN_EXPIRES": self.jwt_access_token_expires,
            "JWT_REMEMBER_TOKEN_EXPIRES": self.jwt_remember_token_expires,
            "JWT_REFRESH_TOKEN_EXPIRES": self.jwt_refresh_token_expires,
        }

    def get_mysql_database_url(self) -> str:
        """Assemble the MySQL database URL."""
        # URL encode the password to handle special characters like @
        encoded_password = quote_plus(self.db_password)
        return f"mysql+pymysql://{self.db_username}:{encoded_password}@{self.db_host}:{self.db_port}/{self.db_name}?charset={self.db_charset}"

    def get_test_database_url(self) -> str:
        """Assemble the MySQL test database URL."""
        # URL encode the password to handle special characters like @
        encoded_password = quote_plus(self.test_db_password)
        return f"mysql+pymysql://{self.test_db_username}:{encoded_password}@{self.test_db_host}:{self.test_db_port}/{self.test_db_name}?charset={self.test_db_charset}"

    def get_database_url(self) -> str:
        """Get database URL - legacy method for backwards compatibility."""
        if self.testing:
            return self.get_test_database_url()
        return self.get_mysql_database_url()

    def __init__(self, **kwargs) -> None:
        """Initialize settings."""
        super().__init__(**kwargs)
        if not self.database_url:
            self.database_url = self.get_mysql_database_url()


# Global settings instance
settings = Settings()
