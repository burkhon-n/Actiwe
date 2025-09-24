#!/usr/bin/env python3
"""
Passenger WSGI entry point for cPanel hosting
This file is specifically designed for cPanel's Passenger WSGI implementation
"""

import os
import sys

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Set environment variables if not already set
if 'ENVIRONMENT' not in os.environ:
    os.environ['ENVIRONMENT'] = 'production'

try:
    # Import the main FastAPI application
    from main import app
    
    # Use uvicorn's WSGI middleware to make FastAPI compatible with WSGI
    from uvicorn.middleware.wsgi import WSGIMiddleware
    
    # Create WSGI application
    application = WSGIMiddleware(app)
    
except ImportError as e:
    # Fallback error handler if imports fail
    def application(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'text/plain')]
        start_response(status, headers)
        error_msg = f"Import Error: {str(e)}\nPython Path: {sys.path}\nCurrent Dir: {current_dir}"
        return [error_msg.encode('utf-8')]

except Exception as e:
    # General error handler
    def application(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'text/plain')]
        start_response(status, headers)
        error_msg = f"Application Error: {str(e)}"
        return [error_msg.encode('utf-8')]

# For debugging purposes (remove in production)
if __name__ == "__main__":
    print("This is the Passenger WSGI entry point.")
    print(f"Current directory: {current_dir}")
    print(f"Python path: {sys.path}")
    print("Import test:")
    try:
        from main import app
        print("✅ FastAPI app imported successfully")
        print(f"App type: {type(app)}")
    except Exception as e:
        print(f"❌ Import failed: {e}")