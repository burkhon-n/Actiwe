# cPanel Deployment Guide for Actiwe Telegram Shop

## Overview

This guide will help you deploy the Actiwe Telegram Shop application on cPanel shared hosting.

## Prerequisites

- cPanel hosting account with Python support
- PostgreSQL database access (or MySQL if needed)
- Domain/subdomain for the application
- Telegram Bot token and channel setup

## Deployment Steps

### Step 1: Upload Files

1. Upload all project files to your cPanel file manager
2. Place files in `public_html/actiwe/` or your desired directory
3. Ensure the following files are present:
   - `passenger_wsgi.py` (Passenger WSGI entry point)
   - `main.py` (FastAPI application)
   - All model files in `models/` directory
   - Template files in `templates/` directory
   - Static files in `static/` directory

### Step 2: Set up Python Environment

1. Go to cPanel → **Python**
2. Create a new Python application:
   - **Python Version**: 3.8+ (use the highest available)
   - **Application Root**: `/actiwe` (or your chosen directory)
   - **Application URL**: `yourdomain.com/actiwe` or subdomain
   - **Application startup file**: `passenger_wsgi.py`
   - **Application Entry Point**: `application`

### Step 3: Install Dependencies

1. In cPanel Python interface, open **Terminal**
2. Run the following commands:

```bash
pip install -r requirements-cpanel.txt
```

### Step 4: Configure Environment Variables

1. Create `.env` file in your application directory:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_db_username
DB_PASSWORD=your_db_password

# Application Configuration  
URL=https://yourdomain.com/actiwe
SECRET_KEY=your-very-secure-secret-key
ENVIRONMENT=production
DEBUG=false

# Telegram Configuration
TOKEN=your_telegram_bot_token
CHANNEL_ID=@your_channel_username
SADMIN=your_telegram_user_id

# File Upload Configuration
MAX_FILE_SIZE_MB=5
ALLOWED_IMAGE_EXTENSIONS=jpg,jpeg,png,webp
```

### Step 5: Database Setup

1. Create PostgreSQL database in cPanel
2. Update database credentials in `.env`
3. Run database migrations:

```bash
python -m alembic upgrade head
```

### Alternative: Standard WSGI Adapter

If Passenger WSGI doesn't work, you can also try the standard `wsgi.py` file:

- **Application startup file**: `wsgi.py`
- **Application Entry Point**: `application`

## Database Configuration

### PostgreSQL Setup (Recommended)

1. Go to cPanel → **PostgreSQL Databases**
2. Create a new database
3. Create a database user and assign to database
4. Note the connection details for `.env` file

### MySQL Alternative (If PostgreSQL not available)

If your cPanel doesn't support PostgreSQL, you'll need to modify the models:

1. Change `database.py`:

```python
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
```

2. Install MySQL connector:

```bash
pip install PyMySQL
```

## SSL Configuration

### Free SSL (Let's Encrypt)

1. Go to cPanel → **SSL/TLS**
2. Enable **Let's Encrypt SSL** for your domain
3. Force HTTPS redirects

### Update Telegram Webhook

After SSL is active, update your bot webhook:

```python
import requests
webhook_url = "https://yourdomain.com/actiwe/webhook"
response = requests.get(f"https://api.telegram.org/bot{YOUR_BOT_TOKEN}/setWebhook?url={webhook_url}")
```

## File Permissions

Set proper permissions for uploaded files:

```bash
chmod 755 static/
chmod 755 static/uploads/
chmod 644 *.py
chmod 600 .env
```

## Troubleshooting

### Common Issues

#### 1. "Module not found" errors

- Ensure all dependencies are installed in the correct Python environment
- Check that the application path is correct

#### 2. Database connection errors

- Verify database credentials in `.env`
- Check if PostgreSQL service is running
- Ensure database user has proper permissions

#### 3. "Permission denied" errors

- Check file permissions (see above)
- Ensure application directory is readable

#### 4. Telegram webhook issues

- Verify SSL certificate is valid
- Check webhook URL is accessible
- Ensure webhook endpoint returns HTTP 200

### Debug Mode

For troubleshooting, temporarily enable debug:

```env
DEBUG=true
```

**Remember to disable debug in production!**

## Testing Deployment

### 1. Check Application Status

Visit: `https://yourdomain.com/actiwe/health`
Should return JSON with status information.

### 2. Test Telegram Integration

1. Send `/start` to your bot
2. Click "Open Web App" button
3. Verify the shop interface loads

### 3. Test Admin Panel

Visit: `https://yourdomain.com/actiwe/admin/`

## Performance Optimization

### 1. Enable Gzip Compression

Add to `.htaccess` in your application directory:

```apache
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css text/js application/javascript application/json
</IfModule>
```

### 2. Cache Static Files

Add to `.htaccess`:

```apache
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType image/jpg "access plus 1 month"
    ExpiresByType image/jpeg "access plus 1 month"
    ExpiresByType image/gif "access plus 1 month"
    ExpiresByType image/png "access plus 1 month"
    ExpiresByType text/css "access plus 1 month"
    ExpiresByType application/pdf "access plus 1 month"
    ExpiresByType text/javascript "access plus 1 month"
    ExpiresByType application/javascript "access plus 1 month"
</IfModule>
```

## Security Considerations

### 1. Environment Variables

- Never commit `.env` to version control
- Use strong passwords and secret keys
- Restrict database user permissions

### 2. File Uploads

- Validate file types and sizes
- Use secure filename handling
- Consider antivirus scanning for uploads

### 3. Access Control

- Implement proper admin authentication
- Use HTTPS for all communications
- Regular security updates

## Monitoring

### 1. Error Logs

Check cPanel error logs regularly:

- cPanel → **Errors**
- Application-specific logs in your Python app interface

### 2. Resource Usage

Monitor resource usage in cPanel to avoid hitting limits:

- CPU usage
- Memory usage
- Database connections

## Backup Strategy

### 1. Database Backups

Set up automatic database backups in cPanel:

- cPanel → **Backup Wizard**
- Schedule regular PostgreSQL dumps

### 2. File Backups

- Backup uploaded images and configuration files
- Consider using cPanel's automatic backup features

## Support

### cPanel-Specific Issues

- Contact your hosting provider's support
- Check cPanel documentation for Python applications

### Application Issues

- Check application logs
- Verify configuration settings
- Test database connectivity

---

## Quick Deployment Checklist

- [ ] Upload all application files
- [ ] Create Python application in cPanel
- [ ] Install dependencies
- [ ] Configure `.env` file
- [ ] Set up database
- [ ] Run database migrations
- [ ] Configure SSL
- [ ] Update Telegram webhook
- [ ] Test application functionality
- [ ] Set up monitoring and backups

**Note**: Some shared hosting providers may have limitations on Python applications or available packages. Contact your hosting provider if you encounter issues with specific dependencies or features.
