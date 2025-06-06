#!/bin/bash

# Test Database Setup Script
# Sets up MySQL test database for running tests

set -e

echo "🧪 Setting up test environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "🚀 Starting test database..."
# Start only the test database service
docker-compose up -d db_test

echo "⏳ Waiting for test database to be ready..."
# Wait for the database to be healthy
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if docker-compose exec -T db_test mysqladmin ping -h localhost --silent; then
        echo "✅ Test database is ready!"
        break
    fi
    attempt=$((attempt + 1))
    echo "⏳ Waiting... (attempt $attempt/$max_attempts)"
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Test database failed to start within timeout period"
    exit 1
fi

echo "🔧 Running test database migrations..."
# Set up test database schema
poetry run python scripts/migrations.py setup-test

echo "✅ Test environment setup complete!"
echo ""
echo "📝 You can now run tests with:"
echo "   poetry run pytest"
echo "   poetry run pytest tests/test_user.py"
echo "   poetry run pytest tests/ -v"
echo ""
echo "🛑 To stop the test database:"
echo "   docker-compose stop db_test" 