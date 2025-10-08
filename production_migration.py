#!/usr/bin/env python3
"""
Production Database Migration Script
Adds missing 'broadcasting' column to admins table
"""

import os
import logging
import sys
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def run_production_migration():
    """Run the migration on production database."""
    try:
        logger.info("🚀 Starting production database migration...")
        
        # Import database modules
        from database import engine
        from sqlalchemy import text, inspect
        
        # Get database inspector
        inspector = inspect(engine)
        
        # Check if admins table exists
        if 'admins' not in inspector.get_table_names():
            logger.error("❌ Admins table not found!")
            return False
        
        # Get current columns in admins table
        columns = inspector.get_columns('admins')
        column_names = [col['name'] for col in columns]
        
        logger.info(f"📋 Current admins table columns: {column_names}")
        
        # Check if broadcasting column already exists
        if 'broadcasting' in column_names:
            logger.info("✅ Broadcasting column already exists!")
            return True
        
        logger.info("🔧 Adding broadcasting column...")
        
        # Create connection
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            try:
                # Step 1: Create enum type if it doesn't exist
                logger.info("Creating broadcasting enum type...")
                conn.execute(text("""
                    DO $$ BEGIN
                        CREATE TYPE broadcasting AS ENUM ('forward', 'copy');
                    EXCEPTION
                        WHEN duplicate_object THEN null;
                    END $$;
                """))
                
                # Step 2: Add the column
                logger.info("Adding broadcasting column...")
                conn.execute(text("""
                    ALTER TABLE admins 
                    ADD COLUMN broadcasting broadcasting;
                """))
                
                # Step 3: Commit transaction
                trans.commit()
                logger.info("✅ Broadcasting column added successfully!")
                
                # Verify the column was added
                inspector = inspect(engine)
                columns = inspector.get_columns('admins')
                column_names = [col['name'] for col in columns]
                
                if 'broadcasting' in column_names:
                    logger.info("✅ Migration completed successfully!")
                    logger.info(f"📋 Updated admins table columns: {column_names}")
                    return True
                else:
                    logger.error("❌ Column was not added successfully!")
                    return False
                    
            except Exception as e:
                trans.rollback()
                logger.error(f"❌ Migration failed, rolling back: {e}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Migration error: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        return False

def main():
    """Main function."""
    logger.info("="*60)
    logger.info("PRODUCTION DATABASE MIGRATION")
    logger.info("="*60)
    
    # Check environment
    env = os.getenv('ENVIRONMENT', 'development')
    logger.info(f"Environment: {env}")
    
    # Run migration
    success = run_production_migration()
    
    if success:
        logger.info("🎉 Migration completed successfully!")
        logger.info("You can now restart your application.")
        return 0
    else:
        logger.error("❌ Migration failed!")
        logger.error("Please check the error messages above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())