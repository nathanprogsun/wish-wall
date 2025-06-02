#!/usr/bin/env python3
"""
Database migrations script using Alembic.
Provides commands for managing database schema changes.
"""

import argparse
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from alembic import command
from alembic.config import Config
from alembic.runtime.environment import EnvironmentContext
from alembic.script import ScriptDirectory

from app.common.database import get_engine
from app.common.logger import get_logger
from app.settings import settings

logger = get_logger(__name__)


def get_alembic_config():
    """Get Alembic configuration."""
    alembic_cfg = Config()

    # Set the script location (migrations directory)
    migrations_dir = project_root / "migrations"
    alembic_cfg.set_main_option("script_location", str(migrations_dir))

    # Set the SQLAlchemy URL from environment or default
    database_url = settings.database_url
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)

    return alembic_cfg


def init_migrations():
    """Initialize Alembic migrations directory."""
    try:
        alembic_cfg = get_alembic_config()
        migrations_dir = project_root / "migrations"

        if migrations_dir.exists():
            logger.warning(f"Migrations directory already exists: {migrations_dir}")
            return

        logger.info("Initializing Alembic migrations...")
        command.init(alembic_cfg, str(migrations_dir))

        # Update env.py to use our models
        env_py_path = migrations_dir / "env.py"
        if env_py_path.exists():
            update_env_py(env_py_path)

        logger.info("✅ Migrations initialized successfully!")
        logger.info(f"📁 Migrations directory: {migrations_dir}")

    except Exception as e:
        logger.error(f"❌ Failed to initialize migrations: {e}")
        sys.exit(1)


def update_env_py(env_py_path: Path):
    """Update the generated env.py file to work with our project."""
    env_content = '''"""Alembic environment configuration."""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import your models
from app.model.user import User
from app.model.message import Message  
from app.model.comment import Comment
from app.common.database import Base

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''

    with open(env_py_path, "w") as f:
        f.write(env_content)

    logger.info("✅ Updated env.py with project configuration")


def generate_migration(message: str):
    """Generate a new migration."""
    try:
        logger.info(f"Generating migration: {message}")
        alembic_cfg = get_alembic_config()
        command.revision(alembic_cfg, message=message, autogenerate=True)
        logger.info("✅ Migration generated successfully!")

    except Exception as e:
        logger.error(f"❌ Failed to generate migration: {e}")
        sys.exit(1)


def upgrade_database():
    """Upgrade database to latest migration."""
    try:
        logger.info("Upgrading database to latest migration...")
        alembic_cfg = get_alembic_config()
        command.upgrade(alembic_cfg, "head")
        logger.info("✅ Database upgraded successfully!")

    except Exception as e:
        logger.error(f"❌ Failed to upgrade database: {e}")
        sys.exit(1)


def downgrade_database():
    """Downgrade database by one migration."""
    try:
        logger.info("Downgrading database by one migration...")
        alembic_cfg = get_alembic_config()
        command.downgrade(alembic_cfg, "-1")
        logger.info("✅ Database downgraded successfully!")

    except Exception as e:
        logger.error(f"❌ Failed to downgrade database: {e}")
        sys.exit(1)


def show_history():
    """Show migration history."""
    try:
        logger.info("Migration history:")
        alembic_cfg = get_alembic_config()
        command.history(alembic_cfg)

    except Exception as e:
        logger.error(f"❌ Failed to show history: {e}")
        sys.exit(1)


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="Database migrations management")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Init command
    subparsers.add_parser("init", help="Initialize migrations")

    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate new migration")
    generate_parser.add_argument(
        "--message", "-m", required=True, help="Migration message"
    )

    # Upgrade command
    subparsers.add_parser("upgrade", help="Upgrade to latest migration")

    # Downgrade command
    subparsers.add_parser("downgrade", help="Downgrade one migration")

    # History command
    subparsers.add_parser("history", help="Show migration history")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    logger.info(f"🚀 Running migration command: {args.command}")

    if args.command == "init":
        init_migrations()
    elif args.command == "generate":
        generate_migration(args.message)
    elif args.command == "upgrade":
        upgrade_database()
    elif args.command == "downgrade":
        downgrade_database()
    elif args.command == "history":
        show_history()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
