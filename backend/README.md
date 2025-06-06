# Wish Wall Backend

A RESTful API backend service for the wish wall application built with Flask and JWT authentication.

## 📁 Project Structure

```
backend/                   # Backend service (Flask + SQLAlchemy)
├── app/                  # Core application code
│   ├── model/            # Data models
│   ├── route/            # API routes
│   ├── service/          # Business logic
│   ├── schema/           # Data validation schemas
│   ├── common/           # Common modules
│   ├── util/             # Utility functions
│   └── data/             # Data processing
├── migrations/           # Database migration files (Alembic)
├── scripts/              # Helper scripts
├── tests/                # Test files
├── pyproject.toml        # Python project configuration
├── poetry.lock           # Dependency lock file
├── docker-compose.yml    # Docker services configuration
├── Dockerfile            # Docker image configuration
├── alembic.ini           # Alembic configuration
├── Makefile              # Development commands
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Poetry for dependency management
- Docker & Docker Compose
- MySQL 8.0+

### 1. Clone and Setup

```bash
git clone <repository-url>
cd wish-wall/backend
```

### 2. Install Dependencies

```bash
make install          # Production dependencies
make dev-install      # Development dependencies
```

### 3. Start Services

```bash
# Start all services (database + API)
make docker-up

# Or start database only
make test-db
```

### 4. Run Database Migrations

```bash
# Check current migration status
make migrations-current

# Apply all pending migrations
make migrations-upgrade

# View migration history
make migrations-history
```

### 5. Create Sample Data

```bash
# Generate seed data (users, wishes, nested comments)
make seed
```

### 6. Run Tests

```bash
# Run all tests
make test

# Run specific test types
make test-unit         # Service layer tests
make test-api          # API endpoint tests
```

## 🛠️ Database Management

### Migration Commands

The project uses **Alembic** for database schema management:

```bash
# View current migration status
make migrations-current

# Show migration history
make migrations-history

# Generate new migration
make migrations-generate MSG="Add new feature"

# Apply migrations
make migrations-upgrade

# Downgrade database
make migrations-downgrade REV="-1"  # Go back 1 step
make migrations-downgrade REV="base"  # Go to initial state

# Reset database (useful for development)
make migrations-reset
```

### Test Database

```bash
# Setup test database with migrations
poetry run python scripts/migrations.py setup-test

# Reset test database
poetry run python scripts/migrations.py reset --database-url "mysql://..."
```

### Advanced Migration Usage

```bash
# Use migrations script directly
poetry run python scripts/migrations.py --help

# Examples:
poetry run python scripts/migrations.py current
poetry run python scripts/migrations.py generate --message "New feature"
poetry run python scripts/migrations.py upgrade --revision "head"
poetry run python scripts/migrations.py downgrade --revision "base"
poetry run python scripts/migrations.py reset
```

## 🧪 Testing

```bash
# Full test suite
make test

# Specific test categories
make test-unit         # Unit tests (services)
make test-api          # Integration tests (API endpoints)

# Test setup
make test-setup        # Setup test environment
make test-reset        # Reset test database
```

## 🔧 Development

### Code Quality

```bash
make format           # Format code with ruff
make lint             # Lint code
make quality          # Run all quality checks
```

### API Testing

The API is available at `http://localhost:8000` when running via Docker.

```bash
# Test authentication
curl -X POST -H "Content-Type: application/json" \
  -d '{"login":"admin","password":"Admin123!"}' \
  http://localhost:8000/api/users/login

# View wishes
curl http://localhost:8000/api/messages/

# Health check
curl http://localhost:8000/health
```

## 📝 Environment Configuration

Create `.env` file with:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USERNAME=root
DB_PASSWORD=your_password
DB_NAME=wish_wall

# Test Database
TEST_DB_HOST=localhost
TEST_DB_PORT=3307
TEST_DB_USERNAME=root
TEST_DB_PASSWORD=your_password
TEST_DB_NAME=wish_wall_test

# JWT Configuration
JWT_SECRET_KEY=your-secret-key
JWT_ACCESS_TOKEN_HOURS=24
JWT_REMEMBER_TOKEN_DAYS=30
JWT_REFRESH_TOKEN_DAYS=7
```

## 🐳 Docker Deployment

```bash
# Build and start all services
make docker-up

# View logs
make docker-logs

# Stop services
make docker-down

# Clean up
make docker-clean
```

The application will be available at:
- API: `http://localhost:8000`
- Database: `localhost:3306` (main), `localhost:3307` (test)

## 📊 Features

- **JWT Authentication**: Secure token-based authentication
- **User Management**: Registration, login, profile management
- **Message System**: Create and manage wish messages
- **Comment System**: Nested comments with unlimited depth
- **Database Migrations**: Alembic-managed schema versioning
- **Testing**: Comprehensive test suite with MySQL integration
- **Docker Support**: Full containerization with Docker Compose
- **API Documentation**: RESTful API with proper error handling

## 🔍 Available Commands

Use `make help` to see all available commands:

```bash
make help
```

This will show all development, testing, migration, and Docker commands available.

## 🏗️ Architecture

- **Flask**: Web framework
- **SQLAlchemy**: ORM with MySQL
- **Alembic**: Database migration management
- **JWT**: Token-based authentication
- **Poetry**: Dependency management
- **Docker**: Containerization
- **pytest**: Testing framework

## 📝 API Documentation

After starting the backend, visit `http://localhost:8000/api/docs` to view the Swagger API documentation.

## 🔧 Configuration

Copy `.env.example` to `.env` and modify the configuration as needed.

Key environment variables:
- `DB_HOST`: Database host (default: localhost)
- `DB_PASSWORD`: Database password
- `SECRET_KEY`: Flask secret key
- `JWT_SECRET_KEY`: JWT token secret key

## 🐳 Docker Deployment

The project includes Docker support for easy deployment:

### Services
- **MySQL Database**: Persistent MySQL 8.0 with automatic initialization
- **Flask Application**: Containerized backend with automatic migration

### Docker Commands
```bash
# Build and start all services
make docker-up

# View service logs
make docker-logs

# Stop all services
make docker-down

# Clean up all Docker resources
make docker-clean
```

### Environment Variables
Docker Compose uses the following key environment variables:
- Database credentials for MySQL container
- JWT secrets for authentication
- Application configuration

## 🧪 Testing

### Run All Tests
```bash
make test
```

### Run Specific Test Types
```bash
make test-unit          # Unit tests only
make test-api           # API tests only
```

### Test Database Setup
```bash
# Start test database
make test-setup

# Run tests with test database
make test
```

## 📄 License

This project is licensed under the MIT License. 