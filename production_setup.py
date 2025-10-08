#!/usr/bin/env python3
"""
Final production setup script for Actiwe E-commerce Bot
This script performs final cleanup and validation for production deployment
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_command(command, description):
    """Run a shell command and return success status"""
    try:
        logger.info(f"🔧 {description}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode == 0:
            logger.info(f"✅ {description} - Success")
            if result.stdout.strip():
                logger.info(f"Output: {result.stdout.strip()}")
            return True
        else:
            logger.error(f"❌ {description} - Failed")
            if result.stderr:
                logger.error(f"Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        logger.error(f"❌ {description} - Exception: {e}")
        return False

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        logger.info(f"✅ {description} exists")
        return True
    else:
        logger.error(f"❌ {description} missing")
        return False

def main():
    """Main production setup function"""
    logger.info("🚀 Actiwe E-commerce Bot - Final Production Setup")
    logger.info("=" * 60)
    
    success_count = 0
    total_checks = 0
    
    # 1. Check required files
    logger.info("\n📁 Checking required files...")
    required_files = [
        ('main.py', 'Main application file'),
        ('bot.py', 'Telegram bot file'),
        ('config.py', 'Configuration file'),
        ('database.py', 'Database connection file'),
        ('migrations.py', 'Migration system'),
        ('start.sh', 'Production startup script'),
        ('.env.example', 'Environment template'),
        ('requirements.txt', 'Dependencies file')
    ]
    
    for filepath, description in required_files:
        total_checks += 1
        if check_file_exists(filepath, description):
            success_count += 1
    
    # 2. Check Python syntax
    logger.info("\n🐍 Checking Python syntax...")
    python_files = ['main.py', 'bot.py', 'config.py', 'database.py', 'migrations.py']
    
    for py_file in python_files:
        total_checks += 1
        if run_command(f"python3 -m py_compile {py_file}", f"Syntax check: {py_file}"):
            success_count += 1
    
    # 3. Clean up cache files
    logger.info("\n🧹 Cleaning up cache files...")
    cleanup_commands = [
        ("find . -name '*.pyc' -delete", "Remove .pyc files"),
        ("find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true", "Remove __pycache__ directories"),
        ("find . -name '.DS_Store' -delete 2>/dev/null || true", "Remove .DS_Store files")
    ]
    
    for command, description in cleanup_commands:
        total_checks += 1
        if run_command(command, description):
            success_count += 1
    
    # 4. Set correct permissions
    logger.info("\n🔒 Setting file permissions...")
    permission_commands = [
        ("chmod +x start.sh", "Make start script executable"),
        ("chmod +x validate_production.py", "Make validation script executable"),
        ("chmod 755 static/", "Set static directory permissions"),
        ("chmod 755 static/uploads/ 2>/dev/null || mkdir -p static/uploads && chmod 755 static/uploads/", "Set uploads directory permissions")
    ]
    
    for command, description in permission_commands:
        total_checks += 1
        if run_command(command, description):
            success_count += 1
    
    # 5. Verify environment
    logger.info("\n⚙️  Checking environment...")
    if Path('.env').exists():
        logger.info("✅ .env file exists")
        total_checks += 1
        success_count += 1
        
        # Check for production settings
        with open('.env', 'r') as f:
            env_content = f.read()
            if 'DEBUG=false' in env_content:
                logger.info("✅ DEBUG is disabled")
            else:
                logger.warning("⚠️  Consider setting DEBUG=false for production")
            
            if 'ENVIRONMENT=production' in env_content:
                logger.info("✅ Environment set to production")
            else:
                logger.warning("⚠️  Consider setting ENVIRONMENT=production")
                
    else:
        logger.warning("⚠️  .env file not found - copy from .env.example")
    
    # 6. Final summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 FINAL PRODUCTION SETUP SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Checks passed: {success_count}/{total_checks}")
    
    if success_count == total_checks:
        logger.info("🎉 All checks passed! Your application is production-ready!")
        logger.info("\n📋 Next steps:")
        logger.info("1. Configure your .env file with production values")
        logger.info("2. Run database migrations: python3 migrations.py")
        logger.info("3. Start the application: ./start.sh")
        logger.info("4. Test all functionality")
        return 0
    else:
        logger.warning(f"⚠️  {total_checks - success_count} checks failed. Please fix issues before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())