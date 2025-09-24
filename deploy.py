#!/usr/bin/env python3
"""
Production deployment script for cPanel hosting.
This script handles database migrations and application startup preparation.
"""

import subprocess
import sys
import os
from pathlib import Path

def log(message):
    """Simple logging function"""
    print(f"🗄️ {message}")

def run_command(command, description):
    """Run a command and handle errors"""
    log(f"{description}...")
    try:
        result = subprocess.run(command, capture_output=True, text=True, cwd=Path(__file__).parent)
        if result.returncode == 0:
            log(f"✅ {description} completed successfully")
            if result.stdout.strip():
                print(result.stdout)
            return True
        else:
            log(f"❌ {description} failed")
            if result.stderr:
                print("Error:", result.stderr)
            return False
    except Exception as e:
        log(f"❌ {description} failed with exception: {e}")
        return False

def main():
    """Main deployment function"""
    log("Starting production deployment...")
    
    # Check if we're in the right directory
    if not os.path.exists('main.py'):
        log("❌ Error: main.py not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Step 1: Check Python environment
    log("Checking Python environment...")
    try:
        from database import engine
        from main import app
        log("✅ Python environment and imports working")
    except Exception as e:
        log(f"❌ Python environment issue: {e}")
        sys.exit(1)
    
    # Step 2: Test database connection
    log("Testing database connection...")
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        log("✅ Database connection successful")
    except Exception as e:
        log(f"❌ Database connection failed: {e}")
        sys.exit(1)
    
    # Step 3: Run database migrations
    success = run_command(
        [sys.executable, '-m', 'alembic', 'upgrade', 'head'],
        "Running database migrations"
    )
    
    if not success:
        log("❌ Migration failed - deployment aborted")
        sys.exit(1)
    
    # Step 4: Verify application can start
    log("Verifying application startup...")
    try:
        from main import app
        log("✅ FastAPI application ready")
    except Exception as e:
        log(f"❌ Application startup failed: {e}")
        sys.exit(1)
    
    # Success!
    log("🎉 Deployment completed successfully!")
    log("Your FastAPI application is ready to run on cPanel with Passenger WSGI")
    log("Use passenger_wsgi.py as your WSGI entry point")
    
    return True

if __name__ == "__main__":
    main()