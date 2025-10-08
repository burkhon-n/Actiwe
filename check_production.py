#!/usr/bin/env python3
"""
Final Production Readiness Check
"""

def check_production_readiness():
    """Check if the application is ready for production"""
    
    print("🚀 ACTIWE E-COMMERCE BOT - PRODUCTION READINESS CHECK")
    print("=" * 60)
    
    checks_passed = 0
    total_checks = 0
    
    # 1. Check core files exist
    import os
    print("\n📁 Checking core files...")
    
    required_files = [
        'main.py', 'bot.py', 'config.py', 'database.py', 'migrations.py',
        'requirements.txt', '.env.example', 'start.sh'
    ]
    
    for file in required_files:
        total_checks += 1
        if os.path.exists(file):
            print(f"✅ {file}")
            checks_passed += 1
        else:
            print(f"❌ {file} missing")
    
    # 2. Check Python syntax
    print("\n🐍 Checking Python syntax...")
    import py_compile
    
    python_files = ['main.py', 'bot.py', 'config.py', 'database.py']
    for file in python_files:
        total_checks += 1
        try:
            py_compile.compile(file, doraise=True)
            print(f"✅ {file} syntax OK")
            checks_passed += 1
        except py_compile.PyCompileError as e:
            print(f"❌ {file} syntax error: {e}")
    
    # 3. Check imports
    print("\n📦 Checking imports...")
    
    modules = [
        ('config', 'Configuration'),
        ('database', 'Database connection'),
        ('models', 'Data models'),
        ('bot', 'Telegram bot'),
        ('main', 'FastAPI application')
    ]
    
    for module, desc in modules:
        total_checks += 1
        try:
            __import__(module)
            print(f"✅ {desc}")
            checks_passed += 1
        except ImportError as e:
            print(f"❌ {desc}: {e}")
    
    # 4. Check database
    print("\n🗄️ Checking database...")
    
    try:
        from database import test_database_connection
        total_checks += 1
        if test_database_connection():
            print("✅ Database connection")
            checks_passed += 1
        else:
            print("❌ Database connection failed")
    except Exception as e:
        print(f"❌ Database test error: {e}")
    
    # 5. Check migrations
    print("\n🔄 Checking migrations...")
    
    try:
        from migrations import DatabaseMigrator
        migrator = DatabaseMigrator()
        results = migrator.run_migrations()
        
        total_checks += 1
        if results['errors'] == 0:
            print("✅ Database migrations")
            checks_passed += 1
            if results['columns_added'] > 0:
                print(f"  📝 Added {results['columns_added']} column(s)")
        else:
            print(f"❌ Migration errors: {results['errors']}")
            
    except Exception as e:
        print(f"❌ Migration check failed: {e}")
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    success_rate = (checks_passed / total_checks) * 100 if total_checks > 0 else 0
    
    print(f"Checks passed: {checks_passed}/{total_checks} ({success_rate:.1f}%)")
    
    if checks_passed == total_checks:
        print("\n🎉 ALL CHECKS PASSED!")
        print("Your application is ready for production deployment!")
        print("\nNext steps:")
        print("1. Configure .env file")
        print("2. Run: ./start.sh")
    elif success_rate >= 80:
        print("\n⚠️  MOSTLY READY")
        print("Fix remaining issues and you're good to go!")
    else:
        print("\n❌ NOT READY")
        print("Please fix the issues above before deployment.")
    
    return checks_passed == total_checks

if __name__ == "__main__":
    import sys
    success = check_production_readiness()
    sys.exit(0 if success else 1)