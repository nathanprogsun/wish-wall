.PHONY: help format lint typecheck quality test install dev-install migrations-init migrations-generate migrations-upgrade migrations-downgrade migrations-history seed

# Default target
help:
	@echo "Available commands:"
	@echo "  make install           - Install dependencies"
	@echo "  make dev-install       - Install development dependencies"
	@echo "  make format            - Format code with ruff"
	@echo "  make lint              - Run ruff linting"
	@echo "  make quality           - Run all quality checks (format + lint)"
	@echo "  make test              - Run all tests"
	@echo "  make test-unit         - Run unit tests only"
	@echo "  make test-api          - Run API tests only"
	@echo ""
	@echo "Database migrations:"
	@echo "  make migrations-init   - Initialize alembic migrations"
	@echo "  make migrations-generate MSG='description' - Generate new migration"
	@echo "  make migrations-upgrade - Upgrade to latest migration"
	@echo "  make migrations-downgrade - Downgrade one migration"
	@echo "  make migrations-history - Show migration history"
	@echo ""
	@echo "Data seeding:"
	@echo "  make seed              - Create seed data (users, messages, 20-level nested comments)"

# Installation
install:
	poetry install --only=main

dev-install:
	poetry install

# Code Quality
format:
	poetry run python scripts/lint.py format

lint:
	poetry run python scripts/lint.py lint

typecheck:
	poetry run python scripts/lint.py typecheck

quality:
	poetry run python scripts/lint.py all

# Testing
test:
	poetry run python -m pytest

test-unit:
	poetry run python -m pytest tests/test_*_service.py -v

test-api:
	poetry run python -m pytest tests/test_api_*.py -v

# Database migrations
migrations-init:
	poetry run python scripts/migrations.py init

migrations-generate:
	@if [ -z "$(MSG)" ]; then \
		echo "Error: Please provide a message with MSG='description'"; \
		echo "Example: make migrations-generate MSG='add user table'"; \
		exit 1; \
	fi
	poetry run python scripts/migrations.py generate --message "$(MSG)"

migrations-upgrade:
	poetry run python scripts/migrations.py upgrade

migrations-downgrade:
	poetry run python scripts/migrations.py downgrade

migrations-history:
	poetry run python scripts/migrations.py history

# Data seeding
seed:
	poetry run python scripts/seed.py

# Development server
dev:
	poetry run python -m app 