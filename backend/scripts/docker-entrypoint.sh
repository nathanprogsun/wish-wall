#!/bin/bash
set -e

echo "🚀 Starting Wish Wall Backend..."

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
while ! mysqladmin ping -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USERNAME" -p"$DB_PASSWORD" --silent; do
    echo "Waiting for database connection..."
    sleep 2
done
echo "✅ Database is ready!"

# Run database migrations
echo "🔧 Running database migrations..."
poetry run alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Database migrations completed successfully"
else
    echo "❌ Database migrations failed"
    exit 1
fi

# Generate seed data
echo "🌱 Generating seed data..."
poetry run python scripts/seed.py

if [ $? -eq 0 ]; then
    echo "✅ Seed data generated successfully"
else
    echo "⚠️  Seed data generation failed, but continuing..."
fi

# Start the application
echo "🌟 Starting Flask application..."
exec "$@" 