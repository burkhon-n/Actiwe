#!/bin/bash
# cPanel dependency installation script with fallbacks

echo "🚀 Installing dependencies for cPanel hosting..."
echo "Trying different PostgreSQL drivers until one works..."

# Try requirements in order of preference
if pip install -r requirements-cpanel.txt; then
    echo "✅ Successfully installed with psycopg2-binary"
    exit 0
elif pip install -r requirements-asyncpg.txt; then
    echo "✅ Successfully installed with asyncpg driver"
    exit 0
elif pip install -r requirements-pg8000.txt; then
    echo "✅ Successfully installed with pg8000 (pure Python) driver"
    exit 0
else
    echo "❌ All installation attempts failed"
    echo ""
    echo "🛠️  Manual troubleshooting options:"
    echo "1. Contact your hosting provider about PostgreSQL headers"
    echo "2. Try: pip install psycopg2-binary==2.9.5"
    echo "3. Consider switching to MySQL (see POSTGRESQL_DRIVER_GUIDE.md)"
    echo "4. Check POSTGRESQL_DRIVER_GUIDE.md for more solutions"
    exit 1
fi