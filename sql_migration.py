#!/usr/bin/env python3
"""
Simple SQL Migration Script
Run this directly on production server to add broadcasting column
"""

import os
import psycopg2
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def get_db_connection():
    """Get database connection from environment variables."""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        return conn
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return None

def run_migration():
    """Run the broadcasting column migration."""
    logger.info("🚀 Starting database migration...")
    
    # Get database connection
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'admins' AND column_name = 'broadcasting';
        """)
        
        if cursor.fetchone():
            logger.info("✅ Broadcasting column already exists!")
            return True
        
        logger.info("🔧 Adding broadcasting column...")
        
        # Create enum type
        cursor.execute("""
            DO $$ BEGIN
                CREATE TYPE broadcasting AS ENUM ('forward', 'copy');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """)
        
        # Add column
        cursor.execute("""
            ALTER TABLE admins 
            ADD COLUMN broadcasting broadcasting;
        """)
        
        # Commit changes
        conn.commit()
        
        # Verify column was added
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'admins' AND column_name = 'broadcasting';
        """)
        
        if cursor.fetchone():
            logger.info("✅ Broadcasting column added successfully!")
            return True
        else:
            logger.error("❌ Column was not added!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = run_migration()
    if success:
        print("🎉 Migration completed! You can now restart your application.")
        exit(0)
    else:
        print("❌ Migration failed! Check the logs above.")
        exit(1)