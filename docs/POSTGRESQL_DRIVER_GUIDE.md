# PostgreSQL Driver Installation Guide for cPanel

## Problem
Getting `pg_config executable not found` error when installing `psycopg2-binary`.

## Solutions (Try in Order)

### Solution 1: Use Alternative Requirements File
```bash
# Instead of requirements-cpanel.txt, try:
pip install -r requirements-asyncpg.txt
```

### Solution 2: Use Pure Python Driver
```bash
# If asyncpg also fails, use pure Python driver:
pip install -r requirements-pg8000.txt
```

### Solution 3: Manual Installation with Specific Versions
```bash
# Try older version of psycopg2-binary
pip install psycopg2-binary==2.9.5

# Or try psycopg2 (not binary)
pip install psycopg2==2.9.8

# Or install without binary
pip install --no-binary psycopg2-binary psycopg2-binary==2.9.8
```

### Solution 4: Install PostgreSQL Development Headers (if you have shell access)
```bash
# On CentOS/RHEL/Rocky Linux
sudo yum install postgresql-devel python3-devel gcc

# On Ubuntu/Debian
sudo apt-get install libpq-dev python3-dev gcc

# Then try installing psycopg2-binary again
pip install psycopg2-binary==2.9.8
```

### Solution 5: Use Pre-compiled Wheel
```bash
# Download wheel from PyPI and upload to your hosting
# Then install locally:
pip install ./psycopg2_binary-2.9.8-cp39-cp39-linux_x86_64.whl
```

## Alternative Database Drivers

### 1. asyncpg (Recommended Alternative)
- **Pros**: Fast, async support, pure Python installation
- **Cons**: Async only, different API
- **Installation**: `pip install asyncpg`

### 2. pg8000 (Pure Python)
- **Pros**: Pure Python, no compilation needed, works everywhere
- **Cons**: Slower than psycopg2, less features
- **Installation**: `pip install pg8000`

## Testing Your Installation

```python
# Test psycopg2
try:
    import psycopg2
    print("✅ psycopg2 available")
except ImportError:
    print("❌ psycopg2 not available")

# Test asyncpg
try:
    import asyncpg
    print("✅ asyncpg available")
except ImportError:
    print("❌ asyncpg not available")

# Test pg8000
try:
    import pg8000
    print("✅ pg8000 available")
except ImportError:
    print("❌ pg8000 not available")
```

## Application Configuration

Your `database.py` is already configured to automatically detect and use the best available driver:

1. **psycopg2** (preferred) → `postgresql://`
2. **asyncpg** (async) → `postgresql+asyncpg://`
3. **pg8000** (pure Python) → `postgresql+pg8000://`

No code changes needed - the app will adapt automatically!

## cPanel-Specific Notes

1. **Check Python version**: Some hosts have multiple Python versions
2. **Use virtual environment**: Always use the cPanel Python app's virtual environment
3. **Contact support**: Some hosts can install PostgreSQL headers for you
4. **Consider alternatives**: Some hosts work better with MySQL

## If All Else Fails: Switch to MySQL

Create `requirements-mysql.txt`:
```
# MySQL version
PyMySQL==1.1.0
# Replace psycopg2-binary with PyMySQL
```

Update database URL in `.env`:
```
DATABASE_URL=mysql+pymysql://username:password@host:port/database
```

## Contact Your Hosting Provider

If none of these solutions work, contact your cPanel hosting provider and ask them to:

1. Install PostgreSQL development headers
2. Install psycopg2-binary in the system Python
3. Provide documentation for PostgreSQL connections on their platform

## Quick Fix for Immediate Deployment

Use this one-liner to install with fallback:
```bash
pip install asyncpg==0.29.0 || pip install pg8000==1.30.3
```

Then use `requirements-asyncpg.txt` or `requirements-pg8000.txt` respectively.