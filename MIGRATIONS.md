# Database Migrations Guide

This document explains how to use the automatic database migration system.

## Overview

The migration system automatically compares your SQLAlchemy models with the actual database schema and adds any missing columns or tables.

## How to Use

### 1. Run Migrations Manually

```bash
python3 migrations.py
```

### 2. Import and Run Programmatically

```python
from migrations import run_migrations

# Run migrations and get results
results = run_migrations()

# Check if any changes were made
if results['columns_added'] > 0 or results['tables_created'] > 0:
    print("Database updated!")
else:
    print("Database is up to date!")
```

### 3. Add to Application Startup

```python
# In your main.py or app initialization
from migrations import run_migrations
import logging

# Run migrations on startup
logger = logging.getLogger(__name__)
try:
    results = run_migrations()
    if results['columns_added'] > 0:
        logger.info(f"Added {results['columns_added']} columns during startup")
except Exception as e:
    logger.error(f"Migration failed: {e}")
```

## What It Does

### ✅ Automatically Handles:
- **Missing columns** - Adds columns that exist in models but not in database
- **Missing tables** - Creates entire tables if they don't exist
- **Enum types** - Creates PostgreSQL enum types automatically
- **Default values** - Applies proper default values
- **Nullable constraints** - Sets correct NULL/NOT NULL constraints
- **Data type mapping** - Converts SQLAlchemy types to PostgreSQL types

### 🔍 Checks These Models:
- `User` → `users` table
- `Admin` → `admins` table  
- `Item` → `items` table
- `Order` → `orders` table
- `CartItem` → `cart_items` table
- `ShopTheme` → `shop_themes` table

### ⚠️ Limitations:
- **No column removal** - Won't drop columns that exist in database but not in models
- **No type changes** - Won't modify existing column types
- **No data migration** - Only handles schema changes, not data transformations

## Examples

### Example 1: Adding a New Column
1. Add column to your model:
```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, nullable=False)
    language_code = Column(String, nullable=True)
    # New column added here
    is_premium = Column(Boolean, default=False, nullable=False)
```

2. Run migration:
```bash
python3 migrations.py
```

3. Output:
```
🔍 Checking model: User (table: users)
📝 Found 1 missing column(s) in users:
   - is_premium: BOOLEAN
✅ Added column 'is_premium' (BOOLEAN) to table 'users'
```

### Example 2: Adding an Enum Column
1. Add enum column to model:
```python
class Admin(Base):
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, nullable=False)
    role = Column(Enum('admin', 'sadmin', name='role'), nullable=False)
    # New enum column
    status = Column(Enum('active', 'inactive', 'suspended', name='admin_status'), nullable=True)
```

2. Run migration:
```bash
python3 migrations.py
```

3. Output:
```
🔍 Checking model: Admin (table: admins)
📝 Found 1 missing column(s) in admins:
   - status: USER-DEFINED
✅ Created enum type 'admin_status'
✅ Added column 'status' (admin_status) to table 'admins'
```

## Integration with Development Workflow

### Option 1: Manual Migration
```bash
# After making model changes
python3 migrations.py
```

### Option 2: Pre-commit Hook
Add to your `.git/hooks/pre-commit`:
```bash
#!/bin/bash
python3 migrations.py
if [ $? -eq 0 ]; then
    echo "✅ Database migrations successful"
else
    echo "❌ Database migrations failed"
    exit 1
fi
```

### Option 3: Application Startup
```python
# In main.py
from migrations import DatabaseMigrator

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    migrator = DatabaseMigrator()
    results = migrator.run_migrations()
    if results['errors']:
        logger.error("Migration errors occurred during startup")
```

## Troubleshooting

### Common Issues:

1. **Permission Errors**
   - Ensure database user has CREATE permissions
   - Check if user can create types and tables

2. **Connection Errors**
   - Verify database connection settings in `config.py`
   - Ensure database server is running

3. **Type Mapping Issues**
   - Check if custom SQLAlchemy types are handled
   - Add custom type mappings if needed

### Debug Mode:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

from migrations import run_migrations
run_migrations()  # Will show detailed SQL queries
```

## Safety Features

- **Transaction-based** - Each table migration runs in its own transaction
- **Rollback on error** - Failed migrations are automatically rolled back
- **Non-destructive** - Never drops columns or tables
- **Validation** - Checks column existence before attempting to add
- **Comprehensive logging** - Detailed logs for debugging

## Best Practices

1. **Always backup** your database before running migrations in production
2. **Test migrations** in development environment first  
3. **Review changes** by checking the logs before applying
4. **Monitor performance** - large tables may take time to add columns
5. **Use transactions** - the system handles this automatically

## Need Help?

- Check the logs for detailed error messages
- Verify your model definitions match expected schema
- Ensure database permissions are sufficient
- Test with a smaller dataset first