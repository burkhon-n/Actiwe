# 🚨 Production Database Migration Instructions

## Problem
Your production server is missing the `broadcasting` column in the `admins` table, causing this error:
```
column admins.broadcasting does not exist
```

## Solution
You need to run a database migration to add the missing column. I've provided 3 different methods below.

---

## Method 1: Python Migration Script (Recommended)

### Upload and run the migration script:

1. **Upload files to production server:**
   - `production_migration.py`
   - `sql_migration.py`

2. **Run the migration:**
```bash
cd /path/to/your/app
python3 production_migration.py
```

**OR if that fails, try the simpler version:**
```bash
python3 sql_migration.py
```

---

## Method 2: Direct SQL (If you have database access)

1. **Upload the SQL file:**
   - `migration.sql`

2. **Run with psql:**
```bash
psql -h [YOUR_DB_HOST] -U [YOUR_DB_USER] -d [YOUR_DB_NAME] -f migration.sql
```

**OR run the SQL directly:**
```sql
-- Create enum type
DO $$ BEGIN
    CREATE TYPE broadcasting AS ENUM ('forward', 'copy');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Add column
ALTER TABLE admins ADD COLUMN broadcasting broadcasting;
```

---

## Method 3: Manual Database Commands

If you have direct database access, run these commands:

```sql
-- Check if column exists
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'admins' AND column_name = 'broadcasting';

-- If not exists, create enum type
CREATE TYPE broadcasting AS ENUM ('forward', 'copy');

-- Add the column
ALTER TABLE admins ADD COLUMN broadcasting broadcasting;

-- Verify it was added
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'admins' 
ORDER BY ordinal_position;
```

---

## Verification

After running the migration, verify it worked:

1. **Check the database:**
```sql
\d admins  -- In psql, shows table structure
```

2. **Test the application:**
```bash
python3 -c "from main import app; print('✅ App starts successfully')"
```

3. **Restart your application server**

---

## Troubleshooting

**If you get permission errors:**
```bash
# Make sure you're using the right database user
echo $DB_USER
echo $DB_HOST

# Test database connection
python3 -c "import psycopg2; conn=psycopg2.connect(host='$DB_HOST', user='$DB_USER', password='$DB_PASSWORD', database='$DB_NAME'); print('✅ DB Connected')"
```

**If the migration fails:**
1. Check if the `admins` table exists
2. Verify your database credentials
3. Make sure you have ALTER permissions on the database

**After successful migration:**
1. Restart your web application
2. Test the admin functionality
3. Check that `/admin/super` route works

---

## Quick Fix Commands

Run these on your production server:

```bash
# 1. Navigate to your app directory
cd /path/to/your/app

# 2. Run the migration
python3 production_migration.py

# 3. Restart your application (adjust command as needed)
sudo systemctl restart your-app-service
# OR
sudo supervisorctl restart your-app
# OR
pkill -f uvicorn && python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
```

---

The error will be fixed once the `broadcasting` column is added to your `admins` table. This is a one-time migration that's safe to run multiple times.