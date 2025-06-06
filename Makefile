.PHONY: help dev install clean backend frontend test lint format stop docker-build docker-up docker-down docker-logs docker-clean

# Default target
help:
	@echo "🎯 Wish Wall - Project Management"
	@echo ""
	@echo "🚀 Quick Start:"
	@echo "  make dev              - Start full-stack services (backend starts 10s first)"
	@echo "  make docker-up        - Start full-stack services with Docker"
	@echo ""
	@echo "🔧 Individual Services:"
	@echo "  make backend          - Start backend development server"
	@echo "  make frontend         - Start frontend development server"
	@echo ""
	@echo "🐳 Docker Management:"
	@echo "  make docker-build     - Build Docker images"
	@echo "  make docker-up        - Start Docker containers"
	@echo "  make docker-down      - Stop Docker containers"
	@echo "  make docker-logs      - View Docker logs"
	@echo "  make docker-clean     - Clean Docker resources"
	@echo ""
	@echo "📦 Project Management:"
	@echo "  make install          - Install all dependencies"
	@echo "  make clean            - Clean cache and temporary files"
	@echo "  make test             - Run all tests"
	@echo "  make lint             - Code linting"
	@echo "  make format           - Format code"
	@echo "  make stop             - Stop all services"
	@echo ""
	@echo "🗄️  Database Management:"
	@echo "  make db-init          - Initialize database"
	@echo "  make db-migrate       - Run database migrations"
	@echo "  make db-seed          - Generate seed data"
	@echo ""
	@echo "📊 Project Information:"
	@echo "  make status           - Check service status"
	@echo "  make logs             - View service logs"

# 🐳 Build Docker images
docker-build:
	@echo "🐳 Building Docker images..."
	@docker-compose build

# 🐳 Start Docker services
docker-up:
	@echo "🐳 Starting Wish Wall full-stack application with Docker..."
	@echo "📍 Frontend: http://localhost:3000"
	@echo "📍 Backend: http://localhost:8000"
	@echo "📍 Database: localhost:3306"
	@echo ""
	@docker-compose up -d
	@echo "✅ All services started"
	@echo "🔍 View logs: make docker-logs"
	@echo "🛑 Stop services: make docker-down"

# 🐳 Stop Docker services
docker-down:
	@echo "🐳 Stopping Docker containers..."
	@docker-compose down
	@echo "✅ All containers stopped"

# 🐳 View Docker logs
docker-logs:
	@echo "🐳 Viewing Docker container logs..."
	@docker-compose logs -f

# 🐳 Clean Docker resources
docker-clean:
	@echo "🐳 Cleaning Docker resources..."
	@docker-compose down -v --remove-orphans
	@docker system prune -f
	@echo "✅ Docker resources cleaned"

# 🚀 Quick start - backend starts 10s first, then frontend
dev:
	@echo "🚀 Starting Wish Wall full-stack application..."
	@echo "📍 Backend: http://localhost:8000"
	@echo "📍 Frontend: http://localhost:3000"
	@echo "📍 API Docs: http://localhost:8000/api/docs"
	@echo ""
	@echo "🔧 Starting backend service..."
	@cd backend && poetry run python -m app &
	@echo "⏳ Waiting for backend service to start (10 seconds)..."
	@sleep 10
	@echo "🎨 Starting frontend service..."
	@cd frontend && npm run dev

# 📦 Install all dependencies
install:
	@echo "📦 Installing dependencies..."
	@echo "  - Installing backend dependencies (Poetry)..."
	@cd backend && poetry install
	@echo "  - Installing frontend dependencies (npm)..."
	@cd frontend && npm install
	@echo "✅ Dependencies installation completed"

# 🧹 Clean project
clean:
	@echo "🧹 Cleaning project cache..."
	@cd backend && poetry run python -c "import shutil; import os; [shutil.rmtree(d, ignore_errors=True) for d in ['.pytest_cache', '__pycache__', '.mypy_cache', '.ruff_cache']]"
	@cd frontend && rm -rf .next node_modules/.cache
	@echo "✅ Cleaning completed"

# 🔧 Backend development service
backend:
	@echo "🔧 Starting backend development service..."
	@echo "📍 Backend service: http://localhost:8000"
	@echo "📍 API Docs: http://localhost:8000/api/docs"
	@echo ""
	@cd backend && poetry run python -m app

# 🎨 Frontend development service
frontend:
	@echo "🎨 Starting frontend development service..."
	@echo "📍 Frontend application: http://localhost:3000"
	@echo ""
	@cd frontend && npm run dev

# 🗄️ Database management
db-init:
	@echo "🗄️ Initializing database..."
	@cd backend && make migrations-init || true
	@cd backend && make migrations-upgrade || true

db-migrate:
	@echo "🗄️ Running database migrations..."
	@cd backend && make migrations-upgrade

db-seed:
	@echo "🌱 Generating seed data..."
	@cd backend && make seed

# 🧪 Testing
test:
	@echo "🧪 Running tests..."
	@echo "  - Backend tests..."
	@cd backend && make test
	@echo "  - Frontend tests..."
	@cd frontend && npm run lint

# 🔍 Code linting
lint:
	@echo "🔍 Code linting..."
	@echo "  - Backend linting..."
	@cd backend && make lint
	@echo "  - Frontend linting..."
	@cd frontend && npm run lint

# ✨ Code formatting
format:
	@echo "✨ Formatting code..."
	@echo "  - Backend formatting..."
	@cd backend && make format
	@echo "  - Frontend formatting (via lint)..."
	@cd frontend && npm run lint

# 🛑 Stop services
stop:
	@echo "🛑 Stopping all services..."
	@pkill -f "python -m app" || true
	@pkill -f "next dev" || true
	@echo "✅ All services stopped"

# 📊 Status check
status:
	@echo "📊 Service status check..."
	@echo "🔧 Backend service (port 8000):"
	@lsof -i :8000 || echo "  ❌ Backend service not running"
	@echo "🎨 Frontend service (port 3000):"
	@lsof -i :3000 || echo "  ❌ Frontend service not running"
	@echo "🐳 Docker container status:"
	@docker-compose ps 2>/dev/null || echo "  ❌ Docker services not running"

# 📜 View logs
logs:
	@echo "📜 Viewing recent logs..."
	@echo "🔧 Backend logs:"
	@cd backend && find logs -name "*.log" -exec tail -n 10 {} \; 2>/dev/null || echo "  ℹ️  No backend logs available"
	@echo "🎨 Frontend logs:"
	@echo "  ℹ️  Frontend logs are output to console" 