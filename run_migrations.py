#!/usr/bin/env python3
"""Production Ready Migration System - Final Version"""

import os
import sys

def main():
    """Main entry point for running migrations"""
    print("🚀 ACTIWE MIGRATION SYSTEM")
    print("==========================")
    
    try:
        from migrations import DatabaseMigrator
        migrator = DatabaseMigrator()
        
        print("✅ Migration system initialized")
        
        # Run migrations
        results = migrator.run_migrations()
        
        # Display results
        print(f"\n📊 MIGRATION SUMMARY")
        print(f"Models processed: {results['models_processed']}/{results['total_models']}")
        print(f"Tables created: {results.get('tables_created', 0)}")
        print(f"Columns added: {results.get('columns_added', 0)}")
        
        if results['errors']:
            print(f"❌ Errors: {len(results['errors'])}")
            for error in results['errors']:
                print(f"  - {error}")
            return False
        else:
            print("✅ All migrations completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)