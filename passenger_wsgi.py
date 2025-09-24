#!/usr/bin/env python3
"""
WSGI Entry Point for cPanel Passenger Hosting
Optimized for FastAPI + Telegram Web App deployment
"""

import sys
import os
import logging

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

try:
    # Import ASGI to WSGI adapter
    from a2wsgi import ASGIMiddleware
    logger.info("✅ a2wsgi imported successfully")
    
    # Import FastAPI application
    from main import app
    logger.info("✅ FastAPI app imported successfully")
    
    # Create WSGI application with optimized settings
    application = ASGIMiddleware(
        app,
        wait_time=30.0  # Wait up to 30 seconds for ASGI app to complete after response
    )
    
    logger.info("✅ WSGI application created successfully")
    logger.info(f"📊 Application type: {type(application)}")
    
except ImportError as e:
    logger.error(f"❌ Import error: {e}")
    logger.error("Please ensure all dependencies are installed: pip install -r requirements.txt")
    raise
except Exception as e:
    logger.error(f"❌ Application startup error: {e}")
    raise
