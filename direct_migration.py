#!/usr/bin/env python3
"""Direct psycopg2 migration - no SQLAlchemy complexity"""

import sys

def direct_migration():
    try:
        # Import psycopg2 directly
        import psycopg2
        
        # Get database connection info
        from config import DB_HOST, DB_NAME, DB_PORT, DB_USER, DB_PASSWORD
        
        # Connect directly with psycopg2
        conn_str = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"
        conn = psycopg2.connect(conn_str)
        conn.autocommit = True
        
        cursor = conn.cursor()
        
        print("🔧 Connected to database, adding broadcasting column...")
        
        # Check if column exists
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'admins' AND column_name = 'broadcasting'
        """)
        
        if cursor.fetchone():
            print("✅ Broadcasting column already exists!")
            cursor.close()
            conn.close()
            return True
        
        print("📝 Column missing, adding it...")
        
        # Create enum if not exists
        cursor.execute("""
            DO $$ 
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'broadcasting') THEN
                    CREATE TYPE broadcasting AS ENUM ('forward', 'copy');
                END IF;
            END $$
        """)
        print("✅ Broadcasting enum ready")
        
        # Add column
        cursor.execute("ALTER TABLE admins ADD COLUMN broadcasting broadcasting")
        print("✅ Broadcasting column added!")
        
        # Verify
        cursor.execute("""
            SELECT column_name, data_type, udt_name 
            FROM information_schema.columns 
            WHERE table_name = 'admins' AND column_name = 'broadcasting'
        """)
        
        result = cursor.fetchone()
        if result:
            print(f"✅ Verification: {result[0]} ({result[1]}, {result[2]})")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = direct_migration()
    if success:
        print("🎉 Direct migration completed successfully!")
        sys.exit(0)
    else:
        print("💥 Direct migration failed!")
        sys.exit(1)