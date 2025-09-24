# cPanel Server Deployment Guide

## 🚀 Quick Deployment Steps

### 1. Install Dependencies (Virtual Environment)

```bash
# Make sure you're in the project directory
cd /home/tgwebuz2/repositories/Actiwe

# Activate virtual environment (if you have one)
source venv/bin/activate

# Install dependencies (without --user flag in venv)
pip install -r requirements.txt

# If not using venv, install with --user
pip install --user -r requirements.txt
```

### 2. Fix File Permissions (Server)

```bash
# Run the permission fixer (handles permission errors gracefully)
python3 fix_permissions.py

# Or manually set key permissions
chmod 755 passenger_wsgi.py deploy_cpanel.sh
chmod 644 Passengerfile.json .htaccess requirements.txt
chmod 644 *.py *.json *.md
chmod 755 static/ templates/
chmod 644 static/uploads/* templates/admin/* templates/errors/*
```

### 3. Test WSGI Application

```bash
# Test if the WSGI app loads correctly
python3 -c "
try:
    from passenger_wsgi import application
    print('✅ WSGI application loaded successfully')
    print(f'Type: {type(application)}')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

### 4. Configure cPanel Python App

1. **Go to cPanel → Python App**
2. **Create New App:**
   - **Python Version:** 3.8+ (use 3.13 if available)
   - **App Directory:** `/home/tgwebuz2/repositories/Actiwe`
   - **App URL:** `/` (or your domain/subdomain)
   - **Application Startup File:** `passenger_wsgi.py`
   - **Application Entry Point:** `application`

3. **Environment Variables:** Add all required variables:
   ```
   DB_HOST=your_postgres_host
   DB_PORT=5432
   DB_NAME=your_database_name
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   URL=https://your-domain.com
   TOKEN=your_telegram_bot_token
   CHANNEL_ID=@your_channel
   SADMIN=your_telegram_id
   SECRET_KEY=your_secret_key
   ENVIRONMENT=production
   DEBUG=false
   ```

4. **Restart the Application**

## 🔧 Troubleshooting Common Issues

### Issue 1: Virtual Environment Dependency Installation Error
```
ERROR: Can not perform a '--user' install. User site-packages are not visible in this virtualenv.
```

**Solution:**
```bash
# If in virtual environment, don't use --user
pip install -r requirements.txt

# If not in virtual environment, use --user
pip install --user -r requirements.txt
```

### Issue 2: Permission Denied on Files
```
❌ Error setting permissions: [Errno 1] Operation not permitted
```

**Solution:** Some system files can't be changed. This is normal for venv files.
```bash
# Set only essential file permissions
chmod 755 passenger_wsgi.py
chmod 644 Passengerfile.json .htaccess
chmod 644 main.py database.py config.py
```

### Issue 3: Import Errors
```
ImportError: No module named 'a2wsgi'
```

**Solution:**
```bash
# Install missing dependencies
pip install a2wsgi==1.10.0
pip install fastapi sqlalchemy psycopg2-binary

# Or install all at once
pip install -r requirements.txt
```

### Issue 4: Database Connection Errors
```
Database connection failed: connect() got an unexpected keyword argument 'connect_timeout'
```

**Solution:** This should be fixed in the updated `database.py`. If still occurs:
```bash
# Test database connection
python3 -c "
from database import test_database_connection
result = test_database_connection()
print('✅ Connected' if result else '❌ Failed')
"
```

## ✅ Deployment Verification

### 1. Check Application Status
```bash
# Test WSGI application
python3 passenger_wsgi.py

# Check if all routes load
python3 -c "from main import app; print(f'Routes: {len(app.routes)}')"
```

### 2. Test Web Access
```bash
# Test health endpoint (replace with your domain)
curl https://your-domain.com/health

# Should return: {"status": "healthy"}
```

### 3. Check Logs
```bash
# Check application logs
tail -f app.log

# Check cPanel error logs
tail -f /home/tgwebuz2/logs/your-domain.com.error.log
```

## 📋 Final Checklist

- [ ] Dependencies installed (a2wsgi, fastapi, sqlalchemy, etc.)
- [ ] File permissions set (755 for executables, 644 for data files)
- [ ] passenger_wsgi.py loads without errors
- [ ] Database connection working
- [ ] Environment variables configured in cPanel
- [ ] Python app configured with correct paths
- [ ] Application restarted in cPanel
- [ ] Health endpoint returns 200 OK
- [ ] Telegram webhook configured and working

## 🎯 Expected Results

After successful deployment:
- ✅ FastAPI application accessible via web
- ✅ All 26+ routes working
- ✅ Database connections stable
- ✅ Telegram bot responding
- ✅ Admin panel accessible
- ✅ File uploads working
- ✅ Order processing functional

Your FastAPI Telegram Web App should now be fully operational on cPanel! 🚀