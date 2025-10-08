#!/usr/bin/env python3
"""Simple broadcasting column migration script"""

import sys
from sqlalchemy import create_engine, text
from config import Config

def add_broadcasting_column():
    """Add broadcasting column with simple approach"""
    try:
        config = Config()
        
        # Create engine from config
        from database import DATABASE_URL
        engine = create_engine(DATABASE_URL)
        
        print("🔧 Adding broadcasting column...")
        
        with engine.connect() as conn:
            # Check if column exists
            result = conn.execute(text("""
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'admins' AND column_name = 'broadcasting'
            """))
            
            if result.fetchone():
                print("✅ Broadcasting column already exists")
                return True
            
            print("📝 Column missing, adding...")
            
            # Create enum and add column in separate statements
            try:
                # Create enum if not exists
                conn.execute(text("""
                    DO $$ 
                    BEGIN
                        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'broadcasting') THEN
                            CREATE TYPE broadcasting AS ENUM ('forward', 'copy');
                        END IF;
                    END $$
                """))
                conn.commit()
                print("✅ Broadcasting enum ready")
                
                # Add column
                conn.execute(text("ALTER TABLE admins ADD COLUMN broadcasting broadcasting"))
                conn.commit()
                print("✅ Broadcasting column added successfully")
                
                return True
                
            except Exception as e:
                print(f"❌ Error during migration: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Failed to add broadcasting column: {e}")
        return False

if __name__ == "__main__":
    success = add_broadcasting_column()
    if success:
        print("🎉 Migration completed successfully!")
        sys.exit(0)
    else:
        print("💥 Migration failed!")
        sys.exit(1)