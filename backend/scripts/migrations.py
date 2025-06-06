#!/usr/bin/env python3
"""
Database Migration Script

Manages database schema using Alembic migrations for both production and test environments.
This script provides a unified interface for common migration operations.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.common.logger import get_logger
from app.settings import settings

logger = get_logger(__name__)


def run_alembic_command(command: list[str], database_url: str = None, description: str = None):
    """Run an Alembic command with optional database URL override."""
    env = os.environ.copy()
    
    if database_url:
        # Set environment variable for custom database URL
        env['DATABASE_URL'] = database_url
        logger.info(f"Using custom database URL: {database_url}")
    
    if description:
        logger.info(f"🔧 {description}")
    
    try:
        result = subprocess.run(
            ["alembic"] + command,
            cwd=project_root,
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.stdout:
            logger.info(result.stdout.strip())
        
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Alembic command failed: {' '.join(command)}")
        if e.stdout:
            logger.error(f"STDOUT: {e.stdout}")
        if e.stderr:
            logger.error(f"STDERR: {e.stderr}")
        return False


def generate_migration(message: str, database_url: str = None):
    """Generate a new migration file."""
    if not message:
        logger.error("❌ Migration message is required")
        return False
    
    logger.info(f"📝 Generating migration: {message}")
    return run_alembic_command(
        ["revision", "--autogenerate", "-m", message],
        database_url,
        f"Generating migration '{message}'"
    )


def upgrade_database(revision: str = "head", database_url: str = None):
    """Upgrade database to a specific revision."""
    logger.info(f"⬆️ Upgrading database to revision: {revision}")
    return run_alembic_command(
        ["upgrade", revision],
        database_url,
        f"Upgrading database to {revision}"
    )


def downgrade_database(revision: str, database_url: str = None):
    """Downgrade database to a specific revision."""
    logger.info(f"⬇️ Downgrading database to revision: {revision}")
    return run_alembic_command(
        ["downgrade", revision],
        database_url,
        f"Downgrading database to {revision}"
    )


def show_current_revision(database_url: str = None):
    """Show current database revision."""
    logger.info("📍 Checking current database revision...")
    return run_alembic_command(
        ["current"],
        database_url,
        "Showing current revision"
    )


def show_migration_history(database_url: str = None):
    """Show migration history."""
    logger.info("📚 Showing migration history...")
    return run_alembic_command(
        ["history"],
        database_url,
        "Showing migration history"
    )


def reset_database(database_url: str = None):
    """Reset database by downgrading to base and upgrading to head."""
    logger.info("🔄 Resetting database...")
    
    # First downgrade to base
    if not downgrade_database("base", database_url):
        return False
    
    # Then upgrade to head
    if not upgrade_database("head", database_url):
        return False
    
    logger.info("✅ Database reset completed")
    return True


def setup_test_database():
    """Set up test database with migrations."""
    test_db_url = settings.get_test_database_url()
    logger.info("🧪 Setting up test database...")
    logger.info(f"Test DB URL: {test_db_url}")
    
    # Check if test database is accessible
    logger.info("📡 Checking test database connection...")
    
    # Upgrade test database to latest
    if not upgrade_database("head", test_db_url):
        logger.error("❌ Failed to set up test database")
        return False
    
    logger.info("✅ Test database setup completed")
    return True


def create_initial_migration():
    """Create initial migration for a fresh database setup."""
    logger.info("🆕 Creating initial migration...")
    
    # Check if any migrations exist
    versions_dir = project_root / "migrations" / "versions"
    if versions_dir.exists() and list(versions_dir.glob("*.py")):
        logger.warning("⚠️ Migrations already exist. Use 'generate' to create new migrations.")
        return False
    
    return generate_migration("Initial database schema")


def main():
    """Main function with CLI interface."""
    parser = argparse.ArgumentParser(description="Database Migration Management")
    parser.add_argument(
        "action",
        choices=[
            "current", "history", "generate", "upgrade", "downgrade", 
            "reset", "setup-test", "init"
        ],
        help="Migration action to perform"
    )
    parser.add_argument(
        "--message", "-m",
        help="Migration message (required for generate)"
    )
    parser.add_argument(
        "--revision", "-r",
        help="Target revision (for upgrade/downgrade)"
    )
    parser.add_argument(
        "--database-url",
        help="Override database URL"
    )
    
    args = parser.parse_args()
    
    try:
        if args.action == "current":
            success = show_current_revision(args.database_url)
            
        elif args.action == "history":
            success = show_migration_history(args.database_url)
            
        elif args.action == "generate":
            if not args.message:
                logger.error("❌ --message is required for generate action")
                sys.exit(1)
            success = generate_migration(args.message, args.database_url)
            
        elif args.action == "upgrade":
            revision = args.revision or "head"
            success = upgrade_database(revision, args.database_url)
            
        elif args.action == "downgrade":
            if not args.revision:
                logger.error("❌ --revision is required for downgrade action")
                sys.exit(1)
            success = downgrade_database(args.revision, args.database_url)
            
        elif args.action == "reset":
            success = reset_database(args.database_url)
            
        elif args.action == "setup-test":
            success = setup_test_database()
            
        elif args.action == "init":
            success = create_initial_migration()
            
        else:
            logger.error(f"❌ Unknown action: {args.action}")
            sys.exit(1)
        
        if not success:
            logger.error(f"❌ Action '{args.action}' failed")
            sys.exit(1)
        
        logger.info(f"✅ Action '{args.action}' completed successfully")
        
    except KeyboardInterrupt:
        logger.info("⏹️ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
