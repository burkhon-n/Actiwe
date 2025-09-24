# cPanel Deployment Troubleshooting Guide

## 🚨 Common cPanel/Passenger Errors and Solutions

### Error #1: Permission Denied (errno=13)
```
An error occurred while trying to access '/home/tgwebuz2/repositories/Actiwe/Passengerfile.json': 
Error opening '/home/tgwebuz2/repositories/Actiwe/Passengerfile.json' for reading: Permission denied (errno=13)
```

**Root Cause:** Apache/Passenger doesn't have read permissions to configuration files.

**Solution:**
1. Run the permission fixer:
   ```bash
   python3 fix_permissions.py
   ```

2. Or manually set permissions:
   ```bash
   # Set directory permissions
   find . -type d -exec chmod 755 {} \;
   
   # Set file permissions
   find . -type f -exec chmod 644 {} \;
   
   # Set executable permissions for scripts
   chmod 755 passenger_wsgi.py
   chmod 755 deploy_cpanel.sh
   ```

3. Verify critical file permissions:
   ```bash
   ls -la passenger_wsgi.py    # Should be 755
   ls -la Passengerfile.json   # Should be 644
   ls -la .htaccess           # Should be 644
   ```

### Error #2: Module Import Errors
```
ImportError: No module named 'a2wsgi'
```

**Solution:**
1. Install dependencies in the correct Python environment:
   ```bash
   pip install --user -r requirements.txt
   ```

2. Or in cPanel Python app terminal:
   ```bash
   pip install a2wsgi==1.10.0
   pip install fastapi
   pip install sqlalchemy
   # ... install all requirements
   ```

### Error #3: Database Connection Issues
```
Database connection failed: connect() got an unexpected keyword argument 'connect_timeout'
```

**Solution:** Already fixed in the optimized database configuration. The system now uses driver-specific connection parameters.

### Error #4: WSGI Application Not Found
```
AttributeError: module 'passenger_wsgi' has no attribute 'application'
```

**Solution:** Ensure `passenger_wsgi.py` contains:
```python
from a2wsgi import ASGIMiddleware
from main import app

application = ASGIMiddleware(app, wait_time=30.0)
```

## 🔧 Optimized Files for cPanel

### 1. passenger_wsgi.py (Optimized)
- ✅ Production logging
- ✅ Error handling
- ✅ Correct a2wsgi parameters
- ✅ cPanel-specific optimizations

### 2. Passengerfile.json (New)
- ✅ Proper Passenger configuration
- ✅ Production environment settings
- ✅ Resource limits for shared hosting

### 3. .htaccess (Enhanced)
- ✅ Security headers
- ✅ CORS for Telegram Web App
- ✅ Static file caching
- ✅ File protection

### 4. deploy_cpanel.sh (New)
- ✅ Automated permission setting
- ✅ Dependency validation
- ✅ WSGI testing
- ✅ Deployment verification

## 📋 Pre-Deployment Checklist

### Before Uploading:
- [ ] Run `python3 fix_permissions.py`
- [ ] Run `./deploy_cpanel.sh`
- [ ] Verify all files have correct permissions
- [ ] Test WSGI application locally
- [ ] Ensure all dependencies are in requirements.txt

### After Uploading to cPanel:
- [ ] Set Python app configuration in cPanel
- [ ] Configure environment variables
- [ ] Restart Python application
- [ ] Check application logs (`app.log`)
- [ ] Test `/health` endpoint
- [ ] Verify Telegram webhook

## 🔍 Debugging Steps

### 1. Check File Permissions
```bash
ls -la passenger_wsgi.py    # Should be -rwxr-xr-x
ls -la Passengerfile.json   # Should be -rw-r--r--
ls -la .htaccess           # Should be -rw-r--r--
```

### 2. Test WSGI Application
```bash
python3 -c "
from passenger_wsgi import application
print('✅ WSGI app loaded successfully')
print(f'Type: {type(application)}')
"
```

### 3. Check Dependencies
```bash
python3 -c "
import a2wsgi
import fastapi
import sqlalchemy
print('✅ All core dependencies available')
"
```

### 4. Validate Configuration
```bash
python3 -c "
from main import app
print(f'✅ FastAPI app loaded: {len(app.routes)} routes')
"
```

## 🚀 Quick Fix Commands

### If you encounter permission errors:
```bash
# Fix all permissions at once
chmod 755 passenger_wsgi.py deploy_cpanel.sh
chmod 644 Passengerfile.json .htaccess requirements.txt
chmod 644 *.py *.json *.md
find static/ -type f -exec chmod 644 {} \; 2>/dev/null
find templates/ -type f -exec chmod 644 {} \; 2>/dev/null
```

### If you encounter import errors:
```bash
# Reinstall dependencies
pip install --user --upgrade -r requirements.txt
```

### If WSGI app fails to load:
```bash
# Test the WSGI application
python3 passenger_wsgi.py
```

## 📞 Support

If you continue to experience issues:

1. Check `app.log` for detailed error messages
2. Verify cPanel Python app settings match your file structure
3. Ensure all environment variables are set correctly
4. Contact your hosting provider if permission issues persist

## 🎯 Expected Result

After following this guide, you should see:
- ✅ Passenger loads `Passengerfile.json` without permission errors
- ✅ WSGI application starts successfully
- ✅ `/health` endpoint returns 200 OK
- ✅ Telegram webhook receives responses
- ✅ All FastAPI routes are accessible

Your FastAPI Telegram Web App should be fully functional on cPanel shared hosting!