"""
Simplified database management inspired by Flask-SQLAlchemy's clean API.
Provides simple session access without Flask context dependency.
"""

from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, sessionmaker, scoped_session, declarative_base
from sqlalchemy.pool import QueuePool

from app.settings import settings
from app.common.logger import get_logger

logger = get_logger(__name__)

# SQLAlchemy ORM Base class - all models inherit from this
Base = declarative_base()

# Global database components
_engine: Engine | None = None
_session_factory: scoped_session | None = None


def init_database(database_url: str = None) -> None:
    """Initialize database engine and session factory."""
    global _engine, _session_factory

    # Use provided URL or get from settings
    db_url = database_url or settings.get_database_url()
    
    # If already initialized with the same URL, skip
    if _engine is not None:
        return

    try:
        logger.info(f"Initializing database: {db_url}")

        _engine = create_engine(
            db_url,
            poolclass=QueuePool,
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
            pool_timeout=settings.db_pool_timeout,
            pool_recycle=settings.db_pool_recycle,
            echo=settings.db_echo,
            pool_pre_ping=True,
            connect_args={
                "charset": settings.db_charset,
                "connect_timeout": 60,
                "read_timeout": 60,
                "write_timeout": 60,
            } if "mysql" in db_url else {},
        )

        _session_factory = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=_engine)
        )

        logger.info("Database initialized successfully")

    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise


def reset_database_connection():
    """Reset database connection (useful for testing)."""
    global _engine, _session_factory
    
    if _session_factory:
        _session_factory.remove()
        _session_factory = None

    if _engine:
        _engine.dispose()
        _engine = None
        
    logger.info("Database connection reset")


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Database session context manager. Simple and clean like Flask-SQLAlchemy.

    Usage:
        # Simple query
        with session() as s:
            user = s.query(User).filter(User.id == "123").first()

        # Create record
        with session() as s:
            user = User(name="John", email="john@example.com")
            s.add(user)
            # Auto-committed on exit

        # Multiple operations
        with session() as s:
            user = s.query(User).filter(User.id == "123").first()
            user.name = "Updated"
            message = Message(content="Hello", author_id=user.id)
            s.add(message)
            # All committed together
    """
    if _session_factory is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")

    db_session = _session_factory()
    try:
        yield db_session
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        logger.error(f"Transaction rolled back: {str(e)}")
        raise
    finally:
        db_session.close()


def get_session() -> Session:
    """
    Get a raw session for advanced use cases.
    Remember to handle commit/rollback and close manually.

    Usage:
        s = get_session()
        try:
            user = s.query(User).filter(User.id == "123").first()
            # ... do something
            s.commit()
        except:
            s.rollback()
            raise
        finally:
            s.close()
    """
    if _session_factory is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")

    return _session_factory()


def get_engine() -> Engine:
    """Get the database engine."""
    if _engine is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return _engine


def close_database() -> None:
    """Close database connections."""
    global _engine, _session_factory

    if _session_factory:
        _session_factory.remove()
        _session_factory = None

    if _engine:
        _engine.dispose()
        _engine = None
        logger.info("Database closed")
