#!/usr/bin/env python3
"""
Production validation script for Actiwe E-commerce Bot
Checks if the application is ready for production deployment
"""

import os
import sys
import importlib.util
from pathlib import Path

def print_status(message, status="info"):
    """Print colored status messages"""
    colors = {
        "info": "\033[94m",      # Blue
        "success": "\033[92m",   # Green
        "warning": "\033[93m",   # Yellow
        "error": "\033[91m",     # Red
        "reset": "\033[0m"       # Reset
    }
    
    icons = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌"
    }
    
    print(f"{colors[status]}{icons[status]} {message}{colors['reset']}")

def check_environment():
    """Check environment configuration"""
    print_status("Checking environment configuration...", "info")
    
    if not os.path.exists('.env'):
        print_status("Missing .env file - copy from .env.example", "error")
        return False
    
    with open('.env', 'r') as f:
        env_content = f.read()
    
    # Check critical variables
    critical_vars = [
        'DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD',
        'URL', 'SECRET_KEY', 'TOKEN', 'SADMIN'
    ]
    
    missing_vars = []
    for var in critical_vars:
        if f"{var}=" not in env_content or f"{var}=your_" in env_content:
            missing_vars.append(var)
    
    if missing_vars:
        print_status(f"Missing environment variables: {', '.join(missing_vars)}", "error")
        return False
    
    # Production checks
    if "DEBUG=true" in env_content:
        print_status("DEBUG is enabled - set DEBUG=false for production", "warning")
    
    if "ENVIRONMENT=development" in env_content:
        print_status("Environment is set to development - set ENVIRONMENT=production", "warning")
    
    print_status("Environment configuration OK", "success")
    return True

def check_dependencies():
    """Check if all required dependencies are available"""
    print_status("Checking dependencies...", "info")
    
    required_modules = [
        'fastapi', 'uvicorn', 'sqlalchemy', 'pg8000',
        'telebot', 'jinja2', 'python_multipart', 'requests'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            if module == 'telebot':
                importlib.import_module('telebot')
            elif module == 'python_multipart':
                importlib.import_module('multipart')
            else:
                importlib.import_module(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print_status(f"Missing dependencies: {', '.join(missing_modules)}", "error")
        print_status("Run: pip install -r requirements.txt", "info")
        return False
    
    print_status("All dependencies available", "success")
    return True

def check_imports():
    """Check if main application modules can be imported"""
    print_status("Checking application imports...", "info")
    
    modules_to_check = [
        'config', 'database', 'bot', 'main',
        'models.User', 'models.Admin', 'models.Item', 'models.Order'
    ]
    
    failed_imports = []
    for module in modules_to_check:
        try:
            importlib.import_module(module)
        except Exception as e:
            failed_imports.append(f"{module}: {str(e)}")
    
    if failed_imports:
        print_status("Import errors found:", "error")
        for error in failed_imports:
            print(f"  - {error}")
        return False
    
    print_status("All modules import successfully", "success")
    return True

def check_database():
    """Check database connectivity"""
    print_status("Checking database connection...", "info")
    
    try:
        from database import test_database_connection
        if test_database_connection():
            print_status("Database connection successful", "success")
            return True
        else:
            print_status("Database connection failed", "error")
            return False
    except Exception as e:
        print_status(f"Database connection error: {e}", "error")
        return False

def check_file_structure():
    """Check if all required files and directories exist"""
    print_status("Checking file structure...", "info")
    
    required_files = [
        'main.py', 'bot.py', 'config.py', 'database.py', 'migrations.py',
        'requirements.txt', '.env.example', 'README.md'
    ]
    
    required_dirs = [
        'models', 'routes', 'templates', 'static', 'static/uploads'
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    missing_dirs = [d for d in required_dirs if not os.path.exists(d)]
    
    if missing_files:
        print_status(f"Missing files: {', '.join(missing_files)}", "error")
        return False
    
    if missing_dirs:
        print_status(f"Missing directories: {', '.join(missing_dirs)}", "error")
        return False
    
    print_status("File structure complete", "success")
    return True

def check_permissions():
    """Check file permissions for uploads directory"""
    print_status("Checking file permissions...", "info")
    
    uploads_dir = Path("static/uploads")
    if not uploads_dir.exists():
        print_status("Uploads directory doesn't exist", "error")
        return False
    
    if not os.access(uploads_dir, os.W_OK):
        print_status("Uploads directory is not writable", "error")
        return False
    
    print_status("File permissions OK", "success")
    return True

def check_migrations():
    """Check if database migrations are up to date"""
    print_status("Checking database migrations...", "info")
    
    try:
        from migrations import DatabaseMigrator
        migrator = DatabaseMigrator()
        results = migrator.run_migrations()
        
        if results['errors']:
            print_status("Migration errors found", "error")
            for error in results['errors']:
                print(f"  - {error}")
            return False
        
        if results['columns_added'] > 0 or results['tables_created'] > 0:
            print_status(f"Applied {results['columns_added']} columns, {results['tables_created']} tables", "success")
        else:
            print_status("Database schema is up to date", "success")
        
        return True
    except Exception as e:
        print_status(f"Migration check failed: {e}", "error")
        return False

def main():
    """Run all production validation checks"""
    print_status("🚀 Actiwe E-commerce Bot - Production Validation", "info")
    print("=" * 60)
    
    checks = [
        ("Environment Configuration", check_environment),
        ("File Structure", check_file_structure),
        ("Dependencies", check_dependencies),
        ("Module Imports", check_imports),
        ("Database Connection", check_database),
        ("Database Migrations", check_migrations),
        ("File Permissions", check_permissions),
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        print(f"\n[{passed + 1}/{total}] {name}")
        if check_func():
            passed += 1
        else:
            print_status(f"Check failed: {name}", "error")
    
    print("\n" + "=" * 60)
    
    if passed == total:
        print_status(f"All {total} checks passed! Ready for production 🎉", "success")
        print_status("You can now run: ./start.sh", "info")
        return 0
    else:
        print_status(f"{passed}/{total} checks passed. Fix issues before deployment.", "error")
        return 1

if __name__ == "__main__":
    sys.exit(main())