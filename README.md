# Actiwe E-commerce Bot# Actiwe Telegram Shop



A complete Telegram e-commerce bot with web admin panel, built with FastAPI and modern web technologies.A modern e-commerce Telegram Web App built with FastAPI, PostgreSQL, and Telegram Bot API. Features a complete admin panel, shopping cart, order management, and production-ready deployment configuration.



## Features## 🚀 Features



### 🤖 Telegram Bot- **Telegram Web App Integration**: Seamless shopping experience within Telegram

- Product catalog with image gallery- **Admin Panel**: Complete product and order management

- Smart shopping cart with size/gender selection- **Shopping Cart**: Advanced cart with size and gender selection

- Order management and status tracking- **Order Processing**: Complete order workflow with customer data collection

- User-friendly Uzbek interface- **Production Ready**: Docker, Nginx, SSL, database migrations

- Admin broadcast system (copy/forward messages)- **Security**: Rate limiting, input validation, secure headers

- **Database Migrations**: Alembic for safe schema updates

### 🌐 Web Admin Panel

- Product management (CRUD operations)## 📋 Requirements

- Order tracking and management

- User analytics and statistics- Python 3.11+

- Theme customization- PostgreSQL 12+

- File upload with image optimization- Telegram Bot Token

- Domain with SSL certificate (for production)

### 🛡️ Security & Performance

- Telegram Web App authentication## 🛠️ Installation

- Rate limiting and CORS protection

- Database connection pooling### Development Setup

- Automatic schema migrations

- Production-ready configuration1. **Clone the repository**

   ```bash

## Quick Start   git clone <repository-url>

   cd Actiwe

### 1. Environment Setup   ```

```bash

# Copy environment template2. **Set up environment**

cp .env.example .env   ```bash

   cp .env.example .env

# Edit configuration   # Edit .env with your configuration

nano .env   ```

```

3. **Configure environment variables**

### 2. Required Environment Variables   ```env

```bash   # Database

# Database   DB_HOST=localhost

DB_HOST=localhost   DB_PORT=5432

DB_PORT=5432   DB_NAME=actiwe_shop

DB_NAME=actiwe_shop   DB_USER=your_user

DB_USER=your_db_user   DB_PASSWORD=your_password

DB_PASSWORD=your_db_password   

   # Application

# Application   URL=https://your-domain.com

URL=https://your-domain.com   SECRET_KEY=your-secret-key

SECRET_KEY=your-secret-key-here   ENVIRONMENT=development

ENVIRONMENT=production   DEBUG=true

DEBUG=false   

   # Telegram

# Telegram   TOKEN=your_bot_token

TOKEN=your_telegram_bot_token   CHANNEL_ID=@your_channel

CHANNEL_ID=@your_channel_id   SADMIN=your_telegram_id

SADMIN=your_telegram_user_id   ```

```

4. **Run development server**

### 3. Database Setup   ```bash

```bash   ./dev.sh

# Install dependencies   ```

pip install -r requirements.txt

### Production Deployment

# Run automatic migrations

python migrations.py#### Option 1: Docker Compose (Recommended)

```

1. **Configure environment**

### 4. Telegram Bot Setup   ```bash

1. Create bot with [@BotFather](https://t.me/botfather)   cp .env.example .env

2. Set your domain for webhook:   # Edit .env with production values

   ```   ```

   /setmenubutton

   🛍 Shop - https://your-domain.com2. **Update nginx.conf**

   ```   - Replace `your-domain.com` with your actual domain

3. Configure Web App URL in bot settings   - Add SSL certificates to `./certs/` directory



### 5. Deploy & Run3. **Deploy**

```bash   ```bash

# Production deployment   docker-compose up -d

python -m uvicorn main:app --host 0.0.0.0 --port 8000   ```



# Or with deployment script#### Option 2: Manual Deployment

chmod +x deploy.sh

./deploy.sh1. **Run deployment script**

```   ```bash

   ./deploy.sh

## Project Structure   ```



```#### Option 3: cPanel Shared Hosting (Optimized)

├── bot.py              # Telegram bot handlers

├── main.py             # FastAPI application1. **Prepare deployment**

├── config.py           # Configuration management   ```bash

├── database.py         # Database connection & ORM   # Fix file permissions

├── migrations.py       # Automatic schema migrations   python3 fix_permissions.py

├── models/             # SQLAlchemy models   

│   ├── User.py   # Run deployment script

│   ├── Admin.py   chmod +x deploy_cpanel.sh

│   ├── Item.py   ./deploy_cpanel.sh

│   ├── Order.py   ```

│   ├── CartItem.py

│   └── ShopTheme.py2. **Upload to cPanel**

├── routes/             # API endpoints   - Upload all files to your domain's document root

│   ├── auth.py         # Authentication   - Ensure `passenger_wsgi.py` has 755 permissions

│   ├── menu.py         # Product catalog   - Ensure `Passengerfile.json` has 644 permissions

│   ├── admin.py        # Admin panel

│   ├── api_admin.py    # Admin API3. **Configure Python App in cPanel**

│   ├── api_user.py     # User API   - App Directory: `/home/yourusername/repositories/Actiwe`

│   └── error.py        # Error handling   - App URL: `/` (or your subdomain)

├── templates/          # HTML templates   - Python Version: 3.8+

├── static/             # Static files & uploads   - Application Startup File: `passenger_wsgi.py`

└── docs/               # Additional documentation

```4. **Set Environment Variables**

   - Configure all required environment variables in cPanel Python app settings

## API Endpoints   - Restart the Python application



### Public Endpoints## 🗄️ Database Management

- `GET /` - Product catalog

- `POST /auth/` - User authentication### Initial Setup

- `POST /checkout` - Order submission```bash

- `GET /health` - Health check# Create initial migration

alembic revision --autogenerate -m "Initial migration"

### Admin Endpoints (Authenticated)

- `GET /admin/` - Admin dashboard# Apply migrations

- `GET /api/admin/stats` - Analyticsalembic upgrade head

- `POST /api/admin/items` - Create product```

- `PUT /api/admin/items/{id}` - Update product

- `DELETE /api/admin/items/{id}` - Delete product### Adding New Columns (Safe for Production)

```bash

### Telegram Webhook# After modifying models, create migration

- `POST /webhook/{token}` - Telegram updatesalembic revision --autogenerate -m "Add new column"



## Database Models# Review the generated migration file

# Apply migration

### User Managementalembic upgrade head

- **User**: Customer profiles and preferences```

- **Admin**: Administrative users with roles

### Migration Commands

### E-commerce```bash

- **Item**: Product catalog with variants# Check current version

- **Order**: Customer orders and statusalembic current

- **CartItem**: Shopping cart management

# Show migration history

### Customizationalembic history

- **ShopTheme**: Branding and appearance

# Downgrade to previous version

## Telegram Bot Commandsalembic downgrade -1

```

### User Commands

- `/start` - Welcome message and catalog access## 📁 Project Structure

- Browse products through inline buttons

- Add items to cart with size/gender selection```

- Complete orders with contact informationActiwe/

├── alembic/                 # Database migrations

### Admin Commands├── models/                  # SQLAlchemy models

- `/message` - Broadcast by copying to all users│   ├── Admin.py

- `/forward` - Broadcast by forwarding to all users│   ├── Item.py

- `/stats` - Get user and order statistics│   ├── CartItem.py

│   ├── Order.py

## Deployment│   └── ShopTheme.py

├── routes/                  # API endpoints

### Requirements│   ├── admin.py            # Admin panel routes

- Python 3.9+│   ├── api_admin.py        # Admin API

- PostgreSQL 12+│   ├── api_user.py         # User API

- SSL certificate for HTTPS│   ├── auth.py             # Authentication

- Domain name for Telegram Web App│   ├── menu.py             # Menu display

│   └── error.py            # Error handling

### Production Configuration├── static/                  # Static files

1. Set `DEBUG=false` in `.env`│   └── uploads/            # Uploaded images

2. Use strong `SECRET_KEY`├── templates/              # HTML templates

3. Configure proper database credentials│   ├── admin/              # Admin templates

4. Set up SSL/HTTPS│   └── errors/             # Error pages

5. Configure domain for Telegram webhook├── main.py                 # FastAPI application

├── bot.py                  # Telegram bot handlers

### Database Migrations├── database.py             # Database configuration

The system automatically handles database schema changes:├── config.py               # Application configuration

```bash├── requirements.txt        # Python dependencies

# Check and apply migrations├── docker-compose.yml      # Docker configuration

python migrations.py├── Dockerfile             # Docker image

├── nginx.conf             # Nginx configuration

# View migration guide├── deploy.sh              # Production deployment

cat MIGRATIONS.md└── dev.sh                 # Development server

``````



### Monitoring## ⚙️ Configuration

- Health endpoint: `/health`

- Logs: Check application logs for errors### Environment Variables

- Database: Monitor connection pool and query performance

| Variable | Description | Required | Default |

## Security Features|----------|-------------|----------|---------|

| `DB_HOST` | Database host | Yes | - |

- **Input Validation**: All user inputs sanitized| `DB_PORT` | Database port | Yes | - |

- **Authentication**: Telegram Web App validation| `DB_NAME` | Database name | Yes | - |

- **Rate Limiting**: API endpoint protection| `DB_USER` | Database user | Yes | - |

- **CORS Protection**: Configured for production| `DB_PASSWORD` | Database password | Yes | - |

- **SQL Injection Prevention**: Parameterized queries| `URL` | Application URL | Yes | - |

- **File Upload Security**: Type and size validation| `TOKEN` | Telegram bot token | Yes | - |

| `CHANNEL_ID` | Orders channel ID | Yes | - |

## Performance Optimizations| `SADMIN` | Super admin Telegram ID | Yes | - |

| `SECRET_KEY` | Encryption key | No | auto-generated |

- **Connection Pooling**: Efficient database connections| `ENVIRONMENT` | Environment mode | No | `development` |

- **Static File Serving**: Optimized file delivery| `DEBUG` | Debug mode | No | `false` |

- **Response Caching**: Reduced database queries| `MAX_FILE_SIZE_MB` | Max upload size | No | `5` |

- **Async Processing**: Non-blocking request handling

- **Image Optimization**: Compressed uploads### Telegram Bot Setup



## Support1. **Create bot**: Message @BotFather on Telegram

2. **Get token**: Save the bot token

### Common Issues3. **Set webhook**: The application automatically sets webhook on startup

1. **Database Connection**: Check credentials and network4. **Create channel**: Create a channel for order notifications

2. **Telegram Webhook**: Verify HTTPS and domain setup5. **Add bot**: Add your bot to the channel as admin

3. **File Uploads**: Check permissions and storage space

4. **Authentication**: Validate bot token and admin ID## 🔒 Security Features



### Logs and Debugging- **Rate Limiting**: API and webhook endpoints protected

```bash- **Input Validation**: All user inputs validated

# View application logs- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries

tail -f app.log- **XSS Protection**: Template escaping and CSP headers

- **CSRF Protection**: Telegram data validation

# Test database connection- **Secure Headers**: HSTS, X-Frame-Options, etc.

python -c "from database import test_database_connection; print(test_database_connection())"- **File Upload Security**: Type and size validation



# Check migrations status## 📊 Monitoring

python migrations.py

```### Health Check

```bash

## Licensecurl https://your-domain.com/health

```

This project is proprietary software. All rights reserved.

### Logs

## Version- Application logs: `error.log`, `access.log`

- Docker logs: `docker-compose logs -f`

**v2.0.0** - Production Ready

- Dual broadcast system## 🧪 Testing

- Automatic migrations

- Enhanced security### Manual Testing

- Performance optimizations1. Start the application

- Complete documentation2. Open your Telegram bot
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