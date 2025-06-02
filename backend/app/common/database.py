"""
Database engine and global session management using native SQLAlchemy.
"""

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

from app.common.logger import get_logger

logger = get_logger(__name__)

# Global database components
Base = declarative_base()
engine: Engine | None = None
SessionLocal: sessionmaker | None = None
db_session: Session | None = None


def init_database(database_url: str, echo: bool = False) -> None:
    """
    Initialize database engine and global session.

    Args:
        database_url: Database connection URL
        echo: Whether to echo SQL queries
    """
    global engine, SessionLocal, db_session

    logger.info(f"Initializing database connection: {database_url}")

    # Configure engine based on database type
    if database_url.startswith("sqlite"):
        # SQLite specific configuration
        engine = create_engine(
            database_url,
            echo=echo,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False, "timeout": 20},
        )
    else:
        # PostgreSQL/MySQL configuration
        engine = create_engine(
            database_url,
            echo=echo,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,
        )

    # Create session factory and global session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create global session
    db_session = SessionLocal()

    logger.info("Database engine initialized successfully")


def get_db_session() -> Session:
    """Get global database session."""
    if db_session is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return db_session


def get_engine() -> Engine:
    """Get database engine."""
    if engine is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return engine
