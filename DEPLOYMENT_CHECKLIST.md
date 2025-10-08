# Production Deployment Checklist

## Pre-Deployment Setup

### ✅ Environment Configuration
- [ ] Copy `.env.example` to `.env`
- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=false`
- [ ] Configure strong `SECRET_KEY`
- [ ] Set production database credentials
- [ ] Configure production domain URL
- [ ] Verify Telegram bot token
- [ ] Set correct admin user ID

### ✅ Database Setup
- [ ] PostgreSQL 12+ installed and running
- [ ] Database and user created
- [ ] Network connectivity verified
- [ ] Run `python migrations.py` to setup schema
- [ ] Verify all tables created successfully

### ✅ Dependencies
- [ ] Python 3.9+ installed
- [ ] Install production dependencies: `pip install -r requirements.txt`
- [ ] Verify all imports work: `python -c "import main"`

### ✅ Security Setup
- [ ] SSL certificate installed
- [ ] HTTPS configured and working
- [ ] Firewall configured (only necessary ports open)
- [ ] File permissions set correctly
- [ ] Static files directory writable

## Telegram Bot Configuration

### ✅ Bot Setup
- [ ] Bot created with @BotFather
- [ ] Bot token configured in `.env`
- [ ] Menu button configured:
  ```
  /setmenubutton
  🛍 Shop - https://your-domain.com
  ```
- [ ] Web App URL configured
- [ ] Webhook will be set automatically on first request

### ✅ Admin Setup
- [ ] Super admin Telegram ID configured in `SADMIN`
- [ ] Test admin access with `/stats` command
- [ ] Verify broadcast functionality (`/message` and `/forward`)

## Application Deployment

### ✅ File Setup
- [ ] All files uploaded to production server
- [ ] Static directory permissions: `chmod 755 static/`
- [ ] Uploads directory permissions: `chmod 755 static/uploads/`
- [ ] Remove any `.pyc` files: `find . -name "*.pyc" -delete`

### ✅ Process Management
- [ ] Configure process manager (systemd, supervisor, etc.)
- [ ] Set up automatic restart on failure
- [ ] Configure log rotation
- [ ] Set up monitoring/alerting

### ✅ Web Server Configuration
Choose one deployment method:

#### Option 1: Direct uvicorn
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Option 2: Behind reverse proxy (Nginx)
- [ ] Nginx configured as reverse proxy
- [ ] SSL termination configured
- [ ] Static file serving configured
- [ ] Rate limiting configured

#### Option 3: cPanel/Shared hosting
- [ ] `passenger_wsgi.py` configured
- [ ] Python version set correctly
- [ ] Dependencies installed in virtual environment

## Testing & Verification

### ✅ Basic Functionality
- [ ] Application starts without errors
- [ ] Health endpoint responds: `curl https://your-domain.com/health`
- [ ] Database connection working
- [ ] Static files served correctly

### ✅ Telegram Integration
- [ ] Bot responds to `/start` command
- [ ] Web app opens from bot menu
- [ ] User authentication works
- [ ] Product catalog loads
- [ ] Shopping cart functionality works
- [ ] Order submission works

### ✅ Admin Panel
- [ ] Admin authentication works
- [ ] Dashboard loads correctly
- [ ] Product management works (CRUD)
- [ ] Order management works
- [ ] File upload functionality works
- [ ] Statistics page loads

### ✅ Performance & Security
- [ ] Response times acceptable (<2s)
- [ ] Memory usage stable
- [ ] No sensitive data in logs
- [ ] Rate limiting working
- [ ] CORS headers configured
- [ ] Error handling working

## Monitoring Setup

### ✅ Application Monitoring
- [ ] Log files configured and rotating
- [ ] Error tracking setup
- [ ] Performance monitoring
- [ ] Uptime monitoring
- [ ] Alert system configured

### ✅ Database Monitoring
- [ ] Connection pool monitoring
- [ ] Query performance monitoring
- [ ] Database backup configured
- [ ] Backup restoration tested

## Maintenance

### ✅ Regular Tasks
- [ ] Monitor application logs
- [ ] Check database performance
- [ ] Monitor disk space (especially uploads)
- [ ] Review security logs
- [ ] Update dependencies periodically

### ✅ Backup Strategy
- [ ] Database backup automated
- [ ] Static files backup configured
- [ ] Configuration files backed up
- [ ] Backup restoration procedure documented
- [ ] Backup integrity testing scheduled

## Troubleshooting

### Common Issues
1. **500 Internal Server Error**
   - Check application logs
   - Verify database connection
   - Check file permissions

2. **Telegram Webhook Issues**
   - Verify HTTPS is working
   - Check webhook URL is accessible
   - Review Telegram webhook logs

3. **Database Connection Issues**
   - Verify credentials in `.env`
   - Check network connectivity
   - Ensure PostgreSQL is running

4. **File Upload Issues**
   - Check directory permissions
   - Verify disk space
   - Check file size limits

### Debug Commands
```bash
# Test database connection
python -c "from database import test_database_connection; print(test_database_connection())"

# Check migrations status
python migrations.py

# Test application import
python -c "import main; print('OK')"

# Test Telegram bot token
curl "https://api.telegram.org/bot$TOKEN/getMe"
```

## Final Checklist

- [ ] All environment variables configured
- [ ] Database schema up to date
- [ ] SSL certificate valid and working
- [ ] Telegram bot configured and responding
- [ ] Admin panel accessible and functional
- [ ] Error handling and logging working
- [ ] Monitoring and alerting configured
- [ ] Backup strategy implemented
- [ ] Documentation updated
- [ ] Team notified of deployment

## Post-Deployment

### ✅ Immediate Actions (First 24 hours)
- [ ] Monitor application logs for errors
- [ ] Test all critical functionality
- [ ] Verify webhook is receiving updates
- [ ] Check database performance
- [ ] Monitor system resources

### ✅ First Week
- [ ] Review error logs daily
- [ ] Monitor user activity and orders
- [ ] Check backup integrity
- [ ] Review performance metrics
- [ ] Gather user feedback

### ✅ Ongoing Maintenance
- [ ] Weekly log review
- [ ] Monthly security updates
- [ ] Quarterly performance review
- [ ] Semi-annual backup restoration test

---

**Deployment Date**: ___________  
**Deployed By**: ___________  
**Version**: v2.0.0  
**Notes**: ___________