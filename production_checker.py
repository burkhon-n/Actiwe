#!/usr/bin/env python3
"""
Production Deployment Checker and Fixer
This script helps identify and fix common production deployment issues.
"""

import os
import sys
import logging
import traceback
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class ProductionChecker:
    def __init__(self):
        self.issues_found = []
        self.fixes_applied = []

    def check_environment_variables(self):
        """Check if all required environment variables are set."""
        logger.info("🔍 Checking environment variables...")
        
        required_vars = [
            'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 'DB_NAME',
            'URL', 'TOKEN', 'CHANNEL_ID', 'SADMIN'
        ]
        
        missing_vars = []
        invalid_vars = []
        
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                missing_vars.append(var)
            elif var == 'CHANNEL_ID':
                try:
                    int(value)
                except (ValueError, TypeError):
                    invalid_vars.append(f"{var}={value} (must be integer)")
        
        if missing_vars:
            self.issues_found.append(f"Missing environment variables: {', '.join(missing_vars)}")
            logger.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        
        if invalid_vars:
            self.issues_found.append(f"Invalid environment variables: {', '.join(invalid_vars)}")
            logger.error(f"❌ Invalid environment variables: {', '.join(invalid_vars)}")
        
        if not missing_vars and not invalid_vars:
            logger.info("✅ All required environment variables are set correctly")
            return True
        
        return False

    def check_file_permissions(self):
        """Check file and directory permissions."""
        logger.info("🔍 Checking file permissions...")
        
        required_paths = [
            'templates/',
            'static/',
            'static/uploads/',
            'templates/index.html',
            'main.py',
            'bot.py',
            'config.py'
        ]
        
        permission_issues = []
        
        for path in required_paths:
            if not os.path.exists(path):
                permission_issues.append(f"Missing: {path}")
            elif not os.access(path, os.R_OK):
                permission_issues.append(f"Not readable: {path}")
            elif path.endswith('/') and not os.access(path, os.W_OK):
                permission_issues.append(f"Directory not writable: {path}")
        
        if permission_issues:
            self.issues_found.extend(permission_issues)
            logger.error(f"❌ Permission issues: {', '.join(permission_issues)}")
            return False
        
        logger.info("✅ All file permissions are correct")
        return True

    def check_dependencies(self):
        """Check if all required Python packages are installed."""
        logger.info("🔍 Checking Python dependencies...")
        
        required_packages = [
            'fastapi', 'uvicorn', 'sqlalchemy', 'psycopg2', 'telebot',
            'python-dotenv', 'jinja2', 'python-multipart', 'httpx'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            self.issues_found.append(f"Missing Python packages: {', '.join(missing_packages)}")
            logger.error(f"❌ Missing packages: {', '.join(missing_packages)}")
            logger.info(f"Run: pip3 install {' '.join(missing_packages)}")
            return False
        
        logger.info("✅ All required Python packages are installed")
        return True

    def test_database_connection(self):
        """Test database connection."""
        logger.info("🔍 Testing database connection...")
        
        try:
            from database import test_database_connection
            if test_database_connection():
                logger.info("✅ Database connection successful")
                return True
            else:
                self.issues_found.append("Database connection failed")
                logger.error("❌ Database connection failed")
                return False
        except Exception as e:
            self.issues_found.append(f"Database test error: {e}")
            logger.error(f"❌ Database test error: {e}")
            return False

    def test_imports(self):
        """Test if all modules can be imported."""
        logger.info("🔍 Testing module imports...")
        
        try:
            from config import TOKEN, URL, CHANNEL_ID, SADMIN
            from database import engine, Base, get_db
            from models import Admin, ShopTheme, User, Item, Order, CartItem
            from bot import bot
            from routes import menu, auth, admin, api_admin, error, api_user
            
            logger.info("✅ All modules imported successfully")
            return True
            
        except Exception as e:
            self.issues_found.append(f"Import error: {e}")
            logger.error(f"❌ Import error: {e}")
            logger.error(traceback.format_exc())
            return False

    def fix_production_settings(self):
        """Apply production fixes."""
        logger.info("🔧 Applying production fixes...")
        
        # Check if running in production
        if os.getenv('ENVIRONMENT') != 'production':
            logger.warning("⚠️  ENVIRONMENT is not set to 'production'")
            logger.info("Consider setting ENVIRONMENT=production in your .env file")
        
        # Create directories if they don't exist
        os.makedirs('static/uploads', exist_ok=True)
        os.makedirs('templates', exist_ok=True)
        
        # Set proper permissions
        try:
            os.chmod('static/uploads', 0o755)
            self.fixes_applied.append("Set uploads directory permissions")
        except Exception as e:
            logger.warning(f"Could not set directory permissions: {e}")
        
        logger.info(f"✅ Applied {len(self.fixes_applied)} fixes")

    def create_systemd_service(self):
        """Create a systemd service file for production deployment."""
        logger.info("🔧 Creating systemd service file...")
        
        current_dir = os.getcwd()
        user = os.getenv('USER', 'www-data')
        
        service_content = f"""[Unit]
Description=Telegram Shop FastAPI Application
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User={user}
WorkingDirectory={current_dir}
Environment=PATH={current_dir}/venv/bin
Environment=PYTHONPATH={current_dir}
ExecStart={current_dir}/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
ExecReload=/bin/kill -HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        try:
            with open('telegram-shop.service', 'w') as f:
                f.write(service_content)
            
            logger.info("✅ Created telegram-shop.service file")
            logger.info("To install:")
            logger.info("sudo cp telegram-shop.service /etc/systemd/system/")
            logger.info("sudo systemctl daemon-reload")
            logger.info("sudo systemctl enable telegram-shop")
            logger.info("sudo systemctl start telegram-shop")
            
            self.fixes_applied.append("Created systemd service file")
            
        except Exception as e:
            logger.error(f"❌ Failed to create service file: {e}")

    def run_all_checks(self):
        """Run all production checks."""
        logger.info("🚀 Starting production deployment checks...")
        
        checks = [
            ("Environment Variables", self.check_environment_variables),
            ("File Permissions", self.check_file_permissions),
            ("Python Dependencies", self.check_dependencies),
            ("Database Connection", self.test_database_connection),
            ("Module Imports", self.test_imports),
        ]
        
        results = {}
        for check_name, check_func in checks:
            logger.info(f"\n--- {check_name} ---")
            results[check_name] = check_func()
        
        # Apply fixes
        logger.info(f"\n--- Applying Fixes ---")
        self.fix_production_settings()
        self.create_systemd_service()
        
        # Summary
        logger.info(f"\n{'='*60}")
        logger.info("PRODUCTION DEPLOYMENT SUMMARY")
        logger.info("="*60)
        
        all_passed = True
        for check_name, passed in results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            logger.info(f"{check_name:20} {status}")
            if not passed:
                all_passed = False
        
        if self.issues_found:
            logger.info(f"\n🔍 ISSUES FOUND ({len(self.issues_found)}):")
            for issue in self.issues_found:
                logger.info(f"  - {issue}")
        
        if self.fixes_applied:
            logger.info(f"\n🔧 FIXES APPLIED ({len(self.fixes_applied)}):")
            for fix in self.fixes_applied:
                logger.info(f"  - {fix}")
        
        if all_passed:
            logger.info("\n🎉 All checks passed! Application should deploy successfully.")
            logger.info("\n📋 NEXT STEPS:")
            logger.info("1. Deploy code to production server")
            logger.info("2. Install systemd service (see commands above)")
            logger.info("3. Start the service: sudo systemctl start telegram-shop")
            logger.info("4. Check logs: sudo journalctl -u telegram-shop -f")
            return 0
        else:
            logger.error("\n❌ Some checks failed. Fix the issues above before deploying.")
            return 1

def main():
    """Main function."""
    checker = ProductionChecker()
    return checker.run_all_checks()

if __name__ == "__main__":
    sys.exit(main())