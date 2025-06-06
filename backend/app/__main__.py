"""
Main application entry point with Flasgger API documentation.
"""

import os

from flasgger import Swagger
from flask import Flask
from flask_cors import CORS

from app.common.database import init_database
from app.common.logger import get_logger, setup_logging
from app.settings import settings

setup_logging()

logger = get_logger(__name__)


def create_app() -> Flask:
    """
    Create and configure Flask application.

    Returns:
        Configured Flask application instance
    """

    logger.info("Initializing Flask application")
    app = Flask(__name__)

    # Load configuration from settings
    app.config.update(settings.to_flask_config())

    # Initialize database
    init_database()

    # Configure CORS
    CORS(
        app,
        origins=settings.cors_origins_list,
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
    )

    # Initialize Swagger documentation
    configure_swagger(app)

    # Register routes
    register_routes(app)

    # Register error handlers
    register_error_handlers(app)

    @app.route("/")
    def index():
        return "<h1>Hi, this is Comments API(with Flask)</h1>"

    # Add health check endpoint
    @app.route("/health")
    def health():
        return {
            "status": "healthy",
            "message": "Comments API is running with JWT authentication",
            "version": "0.1.0",
        }, 200

    logger.info("Flask application initialized successfully")
    return app


def configure_swagger(app: Flask) -> None:
    """
    Configure Swagger API documentation.

    Args:
        app: Flask application instance
    """
    if not settings.swagger_ui_enabled:
        return

    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/apispec.json",
                "rule_filter": lambda _: True,  # All routes
                "model_filter": lambda _: True,  # All models
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs/",
    }

    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Comments Tree API",
            "description": "A RESTful API for infinite nested comments system with JWT authentication",
            "contact": {
                "name": "Developer",
                "email": "dev@example.com",
            },
            "version": "1.0.0",
        },
        "host": "localhost:8000",  # Will be updated in production
        "basePath": "/api",
        "schemes": ["http", "https"],
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: 'Authorization: Bearer {token}'",
            }
        },
        "security": [{"Bearer": []}],
        "consumes": ["application/json"],
        "produces": ["application/json"],
    }

    Swagger(app, config=swagger_config, template=swagger_template)


def register_routes(app: Flask) -> None:
    """Register API routes."""
    from app.route.comment import comment_bp
    from app.route.message import message_bp
    from app.route.user import user_bp

    # Register blueprints with API prefix
    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(message_bp, url_prefix="/api/messages")
    app.register_blueprint(comment_bp, url_prefix="/api/comments")

    logger.info("API routes registered successfully")


def register_error_handlers(app: Flask) -> None:
    """Register global error handlers."""
    import traceback

    from pydantic import ValidationError
    from werkzeug.exceptions import (
        BadRequest,
        MethodNotAllowed,
        NotFound,
        UnsupportedMediaType,
    )

    from app.common.error_code import ErrorCode
    from app.common.exception import APIException
    from app.common.response import error_response

    @app.errorhandler(APIException)
    def api_exception_handler(exc: APIException):
        """Handle APIException with business logic."""
        logger.warning(f"APIException: {exc.message} (code: {exc.error_code})")

        # If the exception has a status_code attribute, use it
        status_code = getattr(exc, "status_code", 500)

        return error_response(
            error_code=exc.error_code, message=exc.message, status=status_code
        )

    @app.errorhandler(NotFound)
    def not_found_handler(exc):
        """Handle 404 Not Found errors."""
        return error_response(error_code=ErrorCode.NOT_FOUND, status=404)

    @app.errorhandler(MethodNotAllowed)
    def method_not_allowed_handler(exc):
        """Handle 405 Method Not Allowed errors."""
        return error_response(
            error_code=ErrorCode.BAD_REQUEST, message="Method not allowed", status=405
        )

    @app.errorhandler(BadRequest)
    def bad_request_handler(exc):
        """Handle 400 Bad Request errors."""
        return error_response(error_code=ErrorCode.BAD_REQUEST, status=400)

    @app.errorhandler(UnsupportedMediaType)
    def unsupported_media_type_handler(exc):
        """Handle 415 Unsupported Media Type errors."""
        return error_response(
            error_code=ErrorCode.BAD_REQUEST,
            message="Unsupported media type",
            status=415,
        )

    @app.errorhandler(ValidationError)
    def validation_exception_handler(exc: ValidationError):
        """Handle Pydantic validation errors."""
        logger.warning(f"ValidationError: {exc}")
        errors = []
        for error in exc.errors():
            field = error["loc"][0] if error["loc"] else "unknown"
            message = error["msg"]
            errors.append(f"{field}: {message}")

        return error_response(
            error_code=ErrorCode.VALIDATION_ERROR,
            message="Validation failed: " + "; ".join(errors),
            status=422,
        )

    @app.errorhandler(ValueError)
    def value_error_handler(exc: ValueError):
        """Handle ValueError exceptions."""
        logger.warning(f"ValueError: {exc!s}")
        return error_response(
            error_code=ErrorCode.BAD_REQUEST, message=str(exc), status=400
        )

    @app.errorhandler(Exception)
    def general_exception_handler(exc: Exception):
        """Handle all other unhandled exceptions as unknown errors."""
        logger.error(f"Unknown error: {type(exc).__name__}: {exc!s}")
        traceback.print_exc()
        return error_response(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="An unexpected error occurred",
            status=500,
        )


def run_server():
    """Run the Flask development server."""

    app = create_app()

    port = int(os.environ.get("PORT", "8000"))
    host = os.environ.get("HOST", "0.0.0.0")

    logger.info(f"Starting server on {host}:{port}")

    app.run(host=host, port=port, debug=settings.debug)


def seed_test_data():
    """Seed the database with test data for development."""
    from app.common.logger import get_logger
    from app.util.seed_data import seed_all

    logger = get_logger(__name__)

    logger.info("Seeding test data")
    app = create_app()
    with app.app_context():
        seed_all()
    logger.info("Test data seeded successfully")


if __name__ == "__main__":
    run_server()
