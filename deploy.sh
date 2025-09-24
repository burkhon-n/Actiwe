#!/bin/bash

# Production deployment script for Actiwe Telegram Shop
# Usage: ./deploy.sh

set -e

echo "🚀 Starting production deployment..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Update pip
echo "⬆️ Updating pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.example to .env and configure your environment variables."
    exit 1
fi

# Run database migrations
echo "🗄️ Running database migrations..."
if [ ! -d "alembic/versions" ] || [ -z "$(ls -A alembic/versions)" ]; then
    echo "Creating initial migration..."
    alembic revision --autogenerate -m "Initial migration"
fi

echo "Applying migrations..."
alembic upgrade head

# Collect static files (if needed)
echo "📁 Organizing static files..."
mkdir -p static/uploads

# Run production server with Gunicorn
echo "🎯 Starting production server..."
echo "Server will be available at: http://0.0.0.0:8000"

# Create gunicorn configuration
cat > gunicorn.conf.py << EOF
# Gunicorn configuration file
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
preload_app = True
keepalive = 2
timeout = 30
graceful_timeout = 30
worker_tmp_dir = "/dev/shm"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
accesslog = "access.log"
errorlog = "error.log"
loglevel = "info"
capture_output = True
enable_stdio_inheritance = True
EOF

# Start with gunicorn
exec gunicorn main:app -c gunicorn.conf.py