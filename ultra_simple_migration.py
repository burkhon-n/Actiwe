#!/usr/bin/env python3
"""Ultra-simple broadcasting column migration"""

import sys

def add_broadcasting_column():
    try:
        print("🔧 Starting broadcasting column migration...")
        
        # Import database components
        from database import engine
        from sqlalchemy import text
        
        print("✅ Database connection established")
        
        # Check if column exists first
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'admins' AND column_name = 'broadcasting'
            """))
            
            if result.fetchone():
                print("✅ Broadcasting column already exists!")
                return True
        
        print("📝 Broadcasting column missing, adding it...")
        
        # Add the column using separate statements
        with engine.connect() as conn:
            # Step 1: Create enum type (if not exists)
            try:
                conn.execute(text("""
                    DO $$ 
                    BEGIN
                        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'broadcasting') THEN
                            CREATE TYPE broadcasting AS ENUM ('forward', 'copy');
                            RAISE NOTICE 'Created broadcasting enum';
                        END IF;
                    END $$
                """))
                conn.commit()
                print("✅ Broadcasting enum ready")
            except Exception as e:
                print(f"⚠️  Enum creation result: {e}")
            
            # Step 2: Add column
            try:
                conn.execute(text("ALTER TABLE admins ADD COLUMN broadcasting broadcasting"))
                conn.commit()
                print("✅ Broadcasting column added!")
                return True
            except Exception as e:
                print(f"❌ Failed to add column: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = add_broadcasting_column()
    if success:
        print("🎉 Migration completed successfully!")
        sys.exit(0)
    else:
        print("💥 Migration failed!")
        sys.exit(1)