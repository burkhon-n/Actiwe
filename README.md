# Actiwe Telegram Shop

A modern e-commerce Telegram Web App built with FastAPI, PostgreSQL, and Telegram Bot API. Features a complete admin panel, shopping cart, order management, and production-ready deployment configuration.

## 🚀 Features

- **Telegram Web App Integration**: Seamless shopping experience within Telegram
- **Admin Panel**: Complete product and order management
- **Shopping Cart**: Advanced cart with size and gender selection
- **Order Processing**: Complete order workflow with customer data collection
- **Production Ready**: Docker, Nginx, SSL, database migrations
- **Security**: Rate limiting, input validation, secure headers
- **Database Migrations**: Alembic for safe schema updates

## 📋 Requirements

- Python 3.11+
- PostgreSQL 12+
- Telegram Bot Token
- Domain with SSL certificate (for production)

## 🛠️ Installation

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Actiwe
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Configure environment variables**
   ```env
   # Database
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=actiwe_shop
   DB_USER=your_user
   DB_PASSWORD=your_password
   
   # Application
   URL=https://your-domain.com
   SECRET_KEY=your-secret-key
   ENVIRONMENT=development
   DEBUG=true
   
   # Telegram
   TOKEN=your_bot_token
   CHANNEL_ID=@your_channel
   SADMIN=your_telegram_id
   ```

4. **Run development server**
   ```bash
   ./dev.sh
   ```

### Production Deployment

#### Option 1: Docker Compose (Recommended)

1. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

2. **Update nginx.conf**
   - Replace `your-domain.com` with your actual domain
   - Add SSL certificates to `./certs/` directory

3. **Deploy**
   ```bash
   docker-compose up -d
   ```

#### Option 2: Manual Deployment

1. **Run deployment script**
   ```bash
   ./deploy.sh
   ```

## 🗄️ Database Management

### Initial Setup
```bash
# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### Adding New Columns (Safe for Production)
```bash
# After modifying models, create migration
alembic revision --autogenerate -m "Add new column"

# Review the generated migration file
# Apply migration
alembic upgrade head
```

### Migration Commands
```bash
# Check current version
alembic current

# Show migration history
alembic history

# Downgrade to previous version
alembic downgrade -1
```

## 📁 Project Structure

```
Actiwe/
├── alembic/                 # Database migrations
├── models/                  # SQLAlchemy models
│   ├── Admin.py
│   ├── Item.py
│   ├── CartItem.py
│   ├── Order.py
│   └── ShopTheme.py
├── routes/                  # API endpoints
│   ├── admin.py            # Admin panel routes
│   ├── api_admin.py        # Admin API
│   ├── api_user.py         # User API
│   ├── auth.py             # Authentication
│   ├── menu.py             # Menu display
│   └── error.py            # Error handling
├── static/                  # Static files
│   └── uploads/            # Uploaded images
├── templates/              # HTML templates
│   ├── admin/              # Admin templates
│   └── errors/             # Error pages
├── main.py                 # FastAPI application
├── bot.py                  # Telegram bot handlers
├── database.py             # Database configuration
├── config.py               # Application configuration
├── requirements.txt        # Python dependencies
├── docker-compose.yml      # Docker configuration
├── Dockerfile             # Docker image
├── nginx.conf             # Nginx configuration
├── deploy.sh              # Production deployment
└── dev.sh                 # Development server
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DB_HOST` | Database host | Yes | - |
| `DB_PORT` | Database port | Yes | - |
| `DB_NAME` | Database name | Yes | - |
| `DB_USER` | Database user | Yes | - |
| `DB_PASSWORD` | Database password | Yes | - |
| `URL` | Application URL | Yes | - |
| `TOKEN` | Telegram bot token | Yes | - |
| `CHANNEL_ID` | Orders channel ID | Yes | - |
| `SADMIN` | Super admin Telegram ID | Yes | - |
| `SECRET_KEY` | Encryption key | No | auto-generated |
| `ENVIRONMENT` | Environment mode | No | `development` |
| `DEBUG` | Debug mode | No | `false` |
| `MAX_FILE_SIZE_MB` | Max upload size | No | `5` |

### Telegram Bot Setup

1. **Create bot**: Message @BotFather on Telegram
2. **Get token**: Save the bot token
3. **Set webhook**: The application automatically sets webhook on startup
4. **Create channel**: Create a channel for order notifications
5. **Add bot**: Add your bot to the channel as admin

## 🔒 Security Features

- **Rate Limiting**: API and webhook endpoints protected
- **Input Validation**: All user inputs validated
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries
- **XSS Protection**: Template escaping and CSP headers
- **CSRF Protection**: Telegram data validation
- **Secure Headers**: HSTS, X-Frame-Options, etc.
- **File Upload Security**: Type and size validation

## 📊 Monitoring

### Health Check
```bash
curl https://your-domain.com/health
```

### Logs
- Application logs: `error.log`, `access.log`
- Docker logs: `docker-compose logs -f`

## 🧪 Testing

### Manual Testing
1. Start the application
2. Open your Telegram bot
3. Click "Start" and open the web app
4. Test product browsing, cart functionality, and order placement

### Database Testing
```bash
# Test database connection
python -c "from database import test_database_connection; print(test_database_connection())"
```

## 🔧 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check PostgreSQL is running
   - Verify connection credentials
   - Ensure database exists

2. **Telegram Webhook Issues**
   - Verify URL is accessible from internet
   - Check SSL certificate is valid
   - Ensure webhook URL ends with `/webhook`

3. **File Upload Errors**
   - Check directory permissions
   - Verify file size limits
   - Ensure `static/uploads` directory exists

4. **Migration Errors**
   - Check database permissions
   - Verify alembic configuration
   - Review migration files for conflicts

### Debug Mode

Set `DEBUG=true` in `.env` to enable:
- Detailed error messages
- Request/response logging
- SQLAlchemy query logging
- Debug endpoints

## 📈 Performance Optimization

### Production Settings
- Use PostgreSQL connection pooling
- Enable Gzip compression (Nginx)
- Set appropriate cache headers
- Use CDN for static files
- Monitor with application metrics

### Database Optimization
- Add indexes for frequently queried fields
- Use database-level constraints
- Regular VACUUM and ANALYZE
- Monitor query performance

## 🚀 Deployment Checklist

### Pre-deployment
- [ ] Configure production environment variables
- [ ] Set up SSL certificates
- [ ] Create database backups
- [ ] Test all functionality
- [ ] Review security settings

### Post-deployment
- [ ] Verify health check endpoint
- [ ] Test Telegram webhook
- [ ] Monitor application logs
- [ ] Set up automated backups
- [ ] Configure monitoring alerts

## 📝 API Documentation

When `DEBUG=true`, API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🆘 Support

For support, please contact the development team or create an issue in the repository.

---

**Note**: This application is production-ready but should be thoroughly tested in your environment before deployment. Always backup your database before applying migrations or updates.