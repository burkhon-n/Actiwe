#!/usr/bin/env python3
"""
Verify production database status
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        print("🔍 Checking database migration status...")
        
        # Test imports
        from database import engine
        from models import Admin
        from sqlalchemy import text
        
        print("✅ All imports successful")
        
        with engine.connect() as conn:
            # Check admins table structure
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'admins' 
                ORDER BY ordinal_position
            """))
            columns = result.fetchall()
            
            print("\n📋 Admins table structure:")
            has_broadcasting = False
            for col in columns:
                nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                print(f"  - {col[0]}: {col[1]} ({nullable})")
                if col[0] == 'broadcasting':
                    has_broadcasting = True
            
            if has_broadcasting:
                print("\n✅ Broadcasting column exists!")
                
                # Check enum values
                result = conn.execute(text("""
                    SELECT enumlabel 
                    FROM pg_enum 
                    WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'broadcasting')
                    ORDER BY enumsortorder
                """))
                enum_values = [row[0] for row in result.fetchall()]
                if enum_values:
                    print(f"✅ Broadcasting enum values: {enum_values}")
                else:
                    print("⚠️ Broadcasting enum not found")
            else:
                print("\n❌ Broadcasting column missing!")
                return 1
        
        # Test model creation
        from database import DatabaseSessionManager
        with DatabaseSessionManager() as db:
            admin_count = db.query(Admin).count()
            print(f"\n✅ Database connection successful - {admin_count} admin(s) found")
        
        print("\n🎉 All checks passed! Database is ready for production.")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())