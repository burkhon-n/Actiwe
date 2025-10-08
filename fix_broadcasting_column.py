#!/usr/bin/env python3
"""
Simple script to manually add the broadcasting column to the admins table
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from database import engine
    from sqlalchemy import text
    
    print("🔧 Manual Broadcasting Column Migration")
    print("=" * 50)
    
    with engine.connect() as conn:
        # Check if admins table exists
        result = conn.execute(text("SELECT to_regclass('public.admins')"))
        table_exists = result.fetchone()[0] is not None
        
        if not table_exists:
            print("❌ Error: admins table does not exist")
            print("Run the main migration first: python3 migrations.py")
            sys.exit(1)
        
        print("✅ Admins table exists")
        
        # Check if broadcasting enum exists
        result = conn.execute(text("SELECT 1 FROM pg_type WHERE typname = 'broadcasting'"))
        enum_exists = result.fetchone() is not None
        
        if not enum_exists:
            print("📝 Creating broadcasting enum type...")
            conn.execute(text("CREATE TYPE broadcasting AS ENUM ('forward', 'copy')"))
            conn.commit()
            print("✅ Created broadcasting enum type")
        else:
            print("✅ Broadcasting enum type already exists")
        
        # Check if broadcasting column exists
        result = conn.execute(text("""
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'admins' AND column_name = 'broadcasting'
        """))
        column_exists = result.fetchone() is not None
        
        if not column_exists:
            print("📝 Adding broadcasting column to admins table...")
            conn.execute(text("ALTER TABLE admins ADD COLUMN broadcasting broadcasting NULL"))
            conn.commit()
            print("✅ Added broadcasting column")
        else:
            print("✅ Broadcasting column already exists")
        
        # Verify the column was added
        result = conn.execute(text("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'admins' 
            ORDER BY ordinal_position
        """))
        columns = result.fetchall()
        
        print("\n📋 Current admins table structure:")
        for col in columns:
            nullable = "NULL" if col[2] == "YES" else "NOT NULL"
            print(f"  - {col[0]}: {col[1]} ({nullable})")
        
        print("\n🎉 Broadcasting column migration completed successfully!")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)