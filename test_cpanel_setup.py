#!/usr/bin/env python3
"""
Test script to verify WSGI setup works correctly
Run this locally before deploying to cPanel
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))



def test_passenger_wsgi_import():
    """Test if Passenger WSGI application can be imported"""
    try:
        from passenger_wsgi import application
        print("✅ Passenger WSGI application imported successfully")
        print(f"Application type: {type(application)}")
        return True
    except Exception as e:
        print(f"❌ Passenger WSGI import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_app():
    """Test if main FastAPI app can be imported"""
    try:
        from main import app
        print("✅ FastAPI application imported successfully")
        print(f"Application type: {type(app)}")
        print(f"Application title: {app.title}")
        return True
    except Exception as e:
        print(f"❌ FastAPI import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database():
    """Test database connectivity"""
    try:
        from database import test_database_connection
        if test_database_connection():
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_models():
    """Test model imports"""
    try:
        from models import Item, Order, CartItem, Admin, ShopTheme
        print("✅ All models imported successfully")
        return True
    except Exception as e:
        print(f"❌ Model import failed: {e}")
        return False

def test_config():
    """Test configuration"""
    try:
        from config import URL, TOKEN, CHANNEL_ID, ENVIRONMENT
        print("✅ Configuration loaded successfully")
        print(f"Environment: {ENVIRONMENT}")
        print(f"URL: {URL}")
        print(f"Has Token: {bool(TOKEN)}")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False



def run_passenger_test_server():
    """Run a test server using Passenger WSGI"""
    try:
        from passenger_wsgi import application
        from wsgiref.simple_server import make_server
        
        print("\n🚀 Starting test Passenger WSGI server on http://localhost:8003")
        print("Visit http://localhost:8003/health to test")
        print("Press Ctrl+C to stop")
        
        with make_server('localhost', 8003, application) as httpd:
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n✋ Server stopped")
    except Exception as e:
        print(f"❌ Passenger WSGI server failed: {e}")

if __name__ == "__main__":
    print("🧪 Testing cPanel WSGI Setup\n")
    
    # Run all tests
    tests = [
        ("Configuration", test_config),
        ("Database", test_database),
        ("Models", test_models),
        ("FastAPI App", test_main_app),
        ("Passenger WSGI", test_passenger_wsgi_import),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- Testing {test_name} ---")
        results.append((test_name, test_func()))
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:15} {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(tests)} tests")
    
    if passed == len(tests):
        print("\n🎉 All tests passed! Ready for cPanel deployment.")
        
        choice = input("\nRun test server? (p=Passenger WSGI, n=No): ").lower()
        if choice == 'p':
            run_passenger_test_server()
    else:
        print("\n⚠️  Some tests failed. Fix issues before deploying to cPanel.")
        print("\nCommon solutions:")
        print("- Check .env file exists and has correct values")
        print("- Verify database is running and accessible")
        print("- Install missing dependencies: pip install -r requirements-cpanel.txt")