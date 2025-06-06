"""
Flask application factory with simplified database initialization.
"""

from flask import Flask
from app.settings import settings
from app.common.database import init_database, close_database
from app.common.logger import get_logger

logger = get_logger(__name__)


def create_app() -> Flask:
    """
    Create and configure Flask application.
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration from settings
    app.config.update(settings.to_flask_config())
    
    # Initialize database
    try:
        init_database()
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
    
    # Register cleanup function for application shutdown
    @app.teardown_appcontext
    def cleanup_database(exception=None):
        """Clean up database resources on application context teardown."""
        if exception:
            logger.error(f"Application context ended with exception: {str(exception)}")
    
    # Register blueprints here
    # from app.routes import message_bp, user_bp
    # app.register_blueprint(message_bp, url_prefix='/api/messages')
    # app.register_blueprint(user_bp, url_prefix='/api/users')
    
    logger.info("Flask application created successfully")
    
    return app


def shutdown_app():
    """
    Shutdown application and clean up resources.
    """
    try:
        close_database()
        logger.info("Application shutdown completed successfully")
    except Exception as e:
        logger.error(f"Error during application shutdown: {str(e)}")
        raise
