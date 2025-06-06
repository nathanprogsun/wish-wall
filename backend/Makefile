.PHONY: help format lint typecheck quality test test-setup test-db test-reset install dev-install migrations-generate migrations-upgrade migrations-downgrade migrations-reset migrations-history migrations-current seed docker-build docker-up docker-down docker-logs

# Default target
help:
	@echo "Available commands:"
	@echo "  make install           - Install dependencies"
	@echo "  make dev-install       - Install development dependencies"
	@echo "  make format            - Format code with ruff"
	@echo "  make lint              - Run ruff linting"
	@echo "  make quality           - Run all quality checks (format + lint)"
	@echo ""
	@echo "Testing commands:"
	@echo "  make test-setup        - Set up test database (Docker + migrations)"
	@echo "  make test              - Run all tests"
	@echo "  make test-unit         - Run unit tests only"
	@echo "  make test-api          - Run API tests only"
	@echo "  make test-db           - Start test database only"
	@echo "  make test-reset        - Reset test database"
	@echo ""
	@echo "Database migrations:"
	@echo "  make migrations-generate MSG='description' - Generate new migration"
	@echo "  make migrations-upgrade - Apply all pending migrations"
	@echo "  make migrations-downgrade REV='-1' - Downgrade to specific revision"
	@echo "  make migrations-history - Show migration history"
	@echo "  make migrations-current - Show current migration"
	@echo "  make migrations-reset  - Reset database (downgrade to base + upgrade)"
	@echo ""
	@echo "Data seeding:"
	@echo "  make seed              - Create seed data with users, messages, and nested comments"
	@echo ""
	@echo "Docker commands:"
	@echo "  make docker-build      - Build Docker images"
	@echo "  make docker-up         - Start all services with Docker Compose"
	@echo "  make docker-down       - Stop all Docker services"
	@echo "  make docker-logs       - Show Docker container logs"
	@echo "  make docker-clean      - Clean up Docker resources"

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
test-setup:
	@echo "🧪 Setting up test environment..."
	./scripts/test-setup.sh

test:
	poetry run python -m pytest

test-unit:
	poetry run python -m pytest tests/test_*_service.py -v

test-api:
	poetry run python -m pytest tests/test_api_*.py -v

test-db:
	@echo "🚀 Starting test database..."
	docker-compose up -d db_test

test-reset:
	@echo "🔄 Resetting test database..."
	poetry run python scripts/migrations.py reset-test

# Database migrations
migrations-generate:
	@if [ -z "$(MSG)" ]; then \
		echo "❌ Error: MSG parameter is required"; \
		echo "Usage: make migrations-generate MSG='Your migration description'"; \
		exit 1; \
	fi
	poetry run python scripts/migrations.py generate --message "$(MSG)"

migrations-upgrade:
	poetry run python scripts/migrations.py upgrade

migrations-downgrade:
	@if [ -z "$(REV)" ]; then \
		echo "❌ Error: REV parameter is required"; \
		echo "Usage: make migrations-downgrade REV='-1' (or specific revision)"; \
		exit 1; \
	fi
	poetry run python scripts/migrations.py downgrade --revision "$(REV)"

migrations-history:
	poetry run python scripts/migrations.py history

migrations-current:
	poetry run python scripts/migrations.py current

migrations-reset:
	poetry run python scripts/migrations.py reset

# Data seeding
seed:
	poetry run python scripts/seed.py

# Development server
dev:
	poetry run python -m app

# Docker commands
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-clean:
	docker-compose down -v --remove-orphans
	docker system prune -f 