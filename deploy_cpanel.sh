#!/bin/bash

# cPanel Deployment Script for FastAPI + Telegram Web App
# Sets proper file permissions and validates deployment

echo "🚀 Starting cPanel deployment for Actiwe..."

# Set working directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 Working directory: $SCRIPT_DIR"

# Function to set file permissions
set_permissions() {
    echo "🔒 Setting file permissions..."
    
    # Set directory permissions (755)
    find . -type d -exec chmod 755 {} \;
    
    # Set file permissions (644)
    find . -type f -exec chmod 644 {} \;
    
    # Set executable permissions for scripts
    chmod 755 passenger_wsgi.py
    chmod 755 deploy_cpanel.sh
    chmod 644 Passengerfile.json
    chmod 644 .htaccess
    
    # Set proper permissions for config files
    chmod 600 .env 2>/dev/null || echo "⚠️  .env file not found"
    
    # Set permissions for static files
    if [ -d "static" ]; then
        chmod -R 644 static/ 2>/dev/null || echo "⚠️  Could not set static file permissions"
        chmod 755 static/ 2>/dev/null || echo "⚠️  Could not set static directory permissions"
        chmod 755 static/uploads/ 2>/dev/null || echo "⚠️  Could not set uploads directory permissions"
        echo "✅ Static file permissions set"
    else
        echo "⚠️  static directory not found"
    fi
    
    # Set permissions for templates
    if [ -d "templates" ]; then
        chmod -R 644 templates/ 2>/dev/null || echo "⚠️  Could not set template file permissions"
        find templates/ -type d -exec chmod 755 {} \; 2>/dev/null || echo "⚠️  Could not set template directory permissions"
        echo "✅ Template permissions set"
    else
        echo "⚠️  templates directory not found"
    fi
    
    echo "✅ File permissions set successfully"
}

# Function to validate Python environment
check_python() {
    echo "🐍 Checking Python environment..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        echo "✅ Python found: $PYTHON_VERSION"
    else
        echo "❌ Python3 not found"
        return 1
    fi
    
    # Check if virtual environment should be used
    if [ -f "venv/bin/activate" ]; then
        echo "🔄 Activating virtual environment..."
        source venv/bin/activate
        PYTHON_VERSION=$(python --version)
        echo "✅ Virtual environment activated: $PYTHON_VERSION"
    fi
}

# Function to install/check dependencies
check_dependencies() {
    echo "📦 Checking dependencies..."
    
    if [ -f "requirements.txt" ]; then
        echo "📋 Installing/updating dependencies..."
        
        # Check if we're in a virtual environment
        if [ -n "$VIRTUAL_ENV" ]; then
            echo "🔧 Installing in virtual environment..."
            pip install -r requirements.txt
        else
            echo "🔧 Installing with --user flag..."
            pip install --user -r requirements.txt
        fi
        
        if [ $? -eq 0 ]; then
            echo "✅ Dependencies installed successfully"
        else
            echo "❌ Failed to install dependencies"
            return 1
        fi
    else
        echo "❌ requirements.txt not found"
        return 1
    fi
}

# Function to validate configuration
validate_config() {
    echo "⚙️  Validating configuration..."
    
    # Check essential files
    essential_files=("passenger_wsgi.py" "main.py" "requirements.txt" "Passengerfile.json" ".htaccess")
    
    for file in "${essential_files[@]}"; do
        if [ -f "$file" ]; then
            echo "✅ $file found"
        else
            echo "❌ $file missing"
            return 1
        fi
    done
    
    # Check if .env exists or environment variables are set
    if [ -f ".env" ]; then
        echo "✅ .env file found"
    else
        echo "⚠️  .env file not found - make sure environment variables are set in cPanel"
    fi
}

# Function to test WSGI application
test_wsgi() {
    echo "🧪 Testing WSGI application..."
    
    python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from passenger_wsgi import application
    print('✅ WSGI application loaded successfully')
    print(f'📊 Application type: {type(application)}')
except Exception as e:
    print(f'❌ WSGI application failed to load: {e}')
    sys.exit(1)
" && echo "✅ WSGI test passed" || echo "❌ WSGI test failed"
}

# Function to display deployment info
show_deployment_info() {
    echo ""
    echo "📋 DEPLOYMENT SUMMARY"
    echo "===================="
    echo "🌐 Application Type: FastAPI + Telegram Web App"
    echo "🔧 WSGI Adapter: a2wsgi (ASGI-to-WSGI conversion)"
    echo "📁 Entry Point: passenger_wsgi.py"
    echo "⚙️  Configuration: Passengerfile.json"
    echo "🛡️  Security: .htaccess with security headers"
    echo ""
    echo "📝 NEXT STEPS FOR CPANEL:"
    echo "========================"
    echo "1. Upload all files to your domain's document root"
    echo "2. Set Python app in cPanel:"
    echo "   - App Directory: /home/tgwebuz2/repositories/Actiwe"
    echo "   - App URL: / (or your subdomain)"
    echo "   - Python Version: 3.8+"
    echo "   - Application Startup File: passenger_wsgi.py"
    echo "3. Set environment variables in cPanel Python app settings"
    echo "4. Restart the Python application"
    echo ""
    echo "🔍 TROUBLESHOOTING:"
    echo "=================="
    echo "- Check app.log for application logs"
    echo "- Verify file permissions (755 for dirs, 644 for files)"
    echo "- Ensure all environment variables are set"
    echo "- Check that PostgreSQL credentials are correct"
    echo ""
}

# Main deployment process
main() {
    echo "🚀 cPanel Deployment Started"
    echo "============================"
    
    set_permissions || { echo "❌ Permission setup failed"; exit 1; }
    check_python || { echo "❌ Python check failed"; exit 1; }
    check_dependencies || { echo "❌ Dependency check failed"; exit 1; }
    validate_config || { echo "❌ Configuration validation failed"; exit 1; }
    test_wsgi || { echo "❌ WSGI test failed"; exit 1; }
    
    show_deployment_info
    
    echo ""
    echo "🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!"
    echo "====================================="
    echo "Your FastAPI Telegram Web App is ready for cPanel hosting!"
}

# Run main function
main