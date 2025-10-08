#!/bin/bash

# Simple script to run the SQL migration directly
echo "🔧 Running SQL migration for broadcasting column..."

# Extract database connection info from the Python environment
DB_INFO=$(python3 -c "
import os
from config import DB_HOST, DB_NAME, DB_PORT, DB_USER, DB_PASSWORD
print(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
" 2>/dev/null)

if [ -z "$DB_INFO" ]; then
    echo "❌ Could not get database connection info"
    exit 1
fi

echo "🔍 Using database connection..."

# Run the SQL script
psql "$DB_INFO" <<'EOF'
-- Create enum if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'broadcasting') THEN
        CREATE TYPE broadcasting AS ENUM ('forward', 'copy');
        RAISE NOTICE 'Created broadcasting enum';
    ELSE
        RAISE NOTICE 'Broadcasting enum already exists';
    END IF;
END
$$;

-- Add column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'admins' AND column_name = 'broadcasting'
    ) THEN
        ALTER TABLE admins ADD COLUMN broadcasting broadcasting;
        RAISE NOTICE 'Added broadcasting column';
    ELSE
        RAISE NOTICE 'Broadcasting column already exists';
    END IF;
END
$$;

-- Verify the result
\echo 'Verification:'
SELECT column_name, data_type, udt_name, is_nullable
FROM information_schema.columns 
WHERE table_name = 'admins' 
ORDER BY ordinal_position;
EOF

if [ $? -eq 0 ]; then
    echo "✅ SQL migration completed successfully!"
else
    echo "❌ SQL migration failed!"
    exit 1
fi