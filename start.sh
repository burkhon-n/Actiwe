#!/bin/bash

# Production startup script for Actiwe E-commerce Bot
# Usage: ./start.sh

echo "🚀 Starting Actiwe E-commerce Bot (Production)"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Please copy .env.example to .env and configure it"
    exit 1
fi

# Check if running as production
if grep -q "DEBUG=true" .env; then
    echo "⚠️  Warning: DEBUG is enabled in .env"
    echo "For production, set DEBUG=false"
fi

# Run database migrations
echo "📊 Running database migrations..."
python3 migrations.py

if [ $? -ne 0 ]; then
    echo "❌ Database migration failed"
    exit 1
fi

# Start the application
echo "🌐 Starting FastAPI application..."
exec python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4