#!/bin/bash

# Development server script for Actiwe Telegram Shop
# Usage: ./dev.sh

set -e

echo "🔧 Starting development server..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Copying .env.example to .env..."
    cp .env.example .env
    echo "Please edit .env file with your configuration."
fi

# Initialize database if needed
echo "🗄️ Initializing database..."
python -c "
from database import test_database_connection, init_database
import asyncio

async def init():
    try:
        if test_database_connection():
            print('✅ Database connection successful')
        else:
            print('❌ Database connection failed')
            exit(1)
    except Exception as e:
        print(f'❌ Database error: {e}')
        exit(1)

asyncio.run(init())
"

# Start development server
echo "🚀 Starting development server..."
echo "Server will be available at: http://localhost:8000"
echo "Press Ctrl+C to stop the server"

# Run with uvicorn for development
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload