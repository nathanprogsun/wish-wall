"""
Simple logger configuration using loguru.
"""

import logging
import sys

from loguru import logger
from loguru._logger import Logger

from app.settings import settings

# Global flag to prevent duplicate initialization
_logging_configured = False


class InterceptHandler(logging.Handler):
    """
    Intercept standard logging and redirect to loguru.

    This handler captures all standard logging calls and forwards them to loguru.
    """

    def emit(self, record: logging.LogRecord) -> None:
        """Forward log record to loguru."""
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller frame
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def configure_logger() -> Logger:
    """
    Configure loguru logger with console output.

    Returns:
        Configured loguru logger instance
    """
    global _logging_configured

    if _logging_configured:
        return logger

    # Remove all default handlers to prevent duplicates
    logger.remove()

    # Simple console format
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> "
        "| <level>{level: <8}</level> "
        "| <level>{message}</level> "
        "| <cyan>{name}:{function}:{line}</cyan>"
    )

    # Add single console handler
    logger.add(
        sys.stderr,  # Use stderr instead of stdout for better compatibility
        level=settings.log_level,
        format=log_format,
        colorize=True,
        enqueue=True,
        catch=True,
    )

    # Optionally add file handler for production
    if not settings.debug:
        logger.add(
            "logs/app.log",
            level=settings.log_level,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message} | {name}:{function}:{line}",
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            enqueue=True,
            catch=True,
        )

    _logging_configured = True
    return logger


def setup_logging() -> None:
    """
    Setup logging for the entire application.

    This function should be called once at application startup to:
    1. Configure loguru with appropriate format and handlers
    2. Intercept standard logging calls and redirect them to loguru
    3. Ensure all logs (Flask, Werkzeug, etc.) use consistent formatting
    """
    global _logging_configured

    if _logging_configured:
        return  # Already configured, skip

    # Configure loguru first
    configure_logger()

    # Create intercept handler once
    intercept_handler = InterceptHandler()

    # Configure root logger to use our handler
    root_logger = logging.getLogger()
    root_logger.handlers.clear()  # Clear existing handlers
    root_logger.addHandler(intercept_handler)
    root_logger.setLevel(logging.NOTSET)

    # Configure specific loggers
    for logger_name in ["werkzeug", "flask.app", "flask"]:
        specific_logger = logging.getLogger(logger_name)
        specific_logger.handlers.clear()  # Clear existing handlers
        specific_logger.addHandler(intercept_handler)
        specific_logger.setLevel(logging.NOTSET)
        specific_logger.propagate = False  # Prevent duplicate propagation


def get_logger(name: str | None = None) -> Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name for identification

    Returns:
        Logger instance

    Note: Call setup_logging() once at application startup before using loggers.
    """
    if not _logging_configured:
        setup_logging()

    return logger.bind(name=name) if name else logger
