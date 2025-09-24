from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.exception_handlers import http_exception_handler
from database import engine, Base, SessionLocal, get_db, test_database_connection, DatabaseSessionManager
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import Admin, ShopTheme
from routes import menu, auth, admin, api_admin, error, api_user
from config import SADMIN, URL, TOKEN, ENVIRONMENT, DEBUG, logger, DB_PASSWORD, CHANNEL_ID
from database import DATABASE_URL
from bot import bot, Update
import contextlib
import logging
import asyncio
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import httpx
from urllib.parse import urlparse

# --- Rate Limiting Middleware ---
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = {}
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old entries
        self.clients = {
            ip: (count, timestamp) for ip, (count, timestamp) in self.clients.items()
            if current_time - timestamp < self.period
        }
        
        # Check rate limit
        if client_ip in self.clients:
            count, timestamp = self.clients[client_ip]
            if current_time - timestamp < self.period and count >= self.calls:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded"}
                )
            self.clients[client_ip] = (count + 1, timestamp)
        else:
            self.clients[client_ip] = (1, current_time)
        
        return await call_next(request)

# --- Security Headers Middleware ---
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"  # Changed from DENY to allow Telegram iframe
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Add HSTS in production
        if ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Only add CSP for non-API routes
        if not request.url.path.startswith("/api") and not request.url.path.startswith("/auth"):
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://telegram.org https://cdn.tailwindcss.com https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.tailwindcss.com; "
                "img-src 'self' data: https:; "
                "font-src 'self' https://fonts.gstatic.com; "
                "connect-src 'self' https://telegram.org https://api.telegram.org; "
                "frame-ancestors https://web.telegram.org https://k.telegram.org;"
            )
        
        return response

# --- Request Logging Middleware ---
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path} - IP: {request.client.host}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {response.status_code} - "
                f"Time: {process_time:.4f}s - "
                f"Path: {request.url.path}"
            )
            
            response.headers["X-Process-Time"] = str(process_time)
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"Request failed: {request.url.path} - Error: {e} - Time: {process_time:.4f}s")
            raise

# --- Database Initialization ---
async def init_database():
    """Initialize database tables and default data."""
    try:
        # Test database connectivity
        if not test_database_connection():
            raise Exception("Database connection test failed")
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created or already exist.")
        
        # Initialize default data
        with DatabaseSessionManager() as db:
            try:
                # Check if default shop theme exists
                if not db.query(ShopTheme).first():
                    default_theme = ShopTheme(name="Actiwe", logo="/static/logo.png")
                    db.add(default_theme)
                    logger.info("Default shop theme created successfully.")
                    
            except SQLAlchemyError as e:
                logger.error(f"Error creating default shop theme: {e}")
                raise
                
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Telegram Shop",
    description="A Telegram Web App for e-commerce",
    version="1.0.0",
    debug=DEBUG,
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None,
)

# --- Exception Handlers ---
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP {exc.status_code} error on {request.url.path}: {exc.detail}")
    return await http_exception_handler(request, exc)

@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    logger.error(f"Internal server error on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# --- Middleware Setup ---
if ENVIRONMENT == "production":
    # Add trusted host middleware in production
    parsed_url = urlparse(URL)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=[parsed_url.hostname, "localhost", "127.0.0.1"]
    )

# Add rate limiting in production
if ENVIRONMENT == "production":
    app.add_middleware(RateLimitMiddleware, calls=100, period=60)

# Add logging middleware
if DEBUG:
    app.add_middleware(RequestLoggingMiddleware)

# Security headers (always enabled)
app.add_middleware(SecurityHeadersMiddleware)

# --- CORS Configuration for Telegram WebApp ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://web.telegram.org",
        "https://k.telegram.org",
    ] if ENVIRONMENT == "production" else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# --- Static Files Mounting ---
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Health Check Endpoint ---
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Test database connection
        db_status = test_database_connection()
        
        return {
            "status": "healthy" if db_status else "unhealthy",
            "database": "connected" if db_status else "disconnected",
            "environment": ENVIRONMENT,
            "timestamp": int(time.time())
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": int(time.time())
            }
        )

# --- Application Lifecycle Events ---
@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    try:
        logger.info(f"Starting Telegram Shop application in {ENVIRONMENT} mode")
        
        # Initialize database
        await init_database()
        
        # Set up Telegram webhook
        webhook_url = f"{URL}/webhook"
        await bot.set_webhook(url=webhook_url)
        logger.info(f"Telegram webhook set to {webhook_url}")
        
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    try:
        logger.info("Shutting down Telegram Shop application")
        
        # Remove webhook
        await bot.remove_webhook()
        logger.info("Telegram webhook removed")
        
        # Close bot session
        await bot.close_session()
        
        logger.info("Application shutdown completed")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

# --- Telegram Webhook Endpoints ---
@app.get("/webhook")
async def get_webhook_info(request: Request):
    """Get current webhook information."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.telegram.org/bot{TOKEN}/getWebhookInfo"
            )
            return response.json()
    except Exception as e:
        logger.error(f"Failed to get webhook info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get webhook info")

@app.post("/webhook")
async def webhook_handler(request: Request):
    """Handle incoming Telegram webhook updates."""
    try:
        json_data = await request.json()
        update = Update.de_json(json_data)
        
        # Process update asynchronously to avoid blocking
        asyncio.create_task(bot.process_new_updates([update]))
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Error processing webhook update: {e}")
        return JSONResponse(
            status_code=200,  # Always return 200 to avoid Telegram retries
            content={"status": "error", "message": str(e)}
        )

# --- Root Endpoint ---
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main application entry point."""
    try:
        with open("templates/index.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        logger.error("index.html template not found")
        raise HTTPException(status_code=500, detail="Template not found")
    except Exception as e:
        logger.error(f"Error serving root page: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# --- Include Application Routers ---
app.include_router(menu.router, tags=["Menu"])
app.include_router(auth.router, tags=["Authentication"])
app.include_router(admin.router, tags=["Admin"])
app.include_router(api_admin.router, tags=["Admin API"])
app.include_router(api_user.router, tags=["User API"])
app.include_router(error.router, tags=["Error Handling"])

# --- Development Tools ---
if DEBUG:
    @app.get("/debug/config")
    async def debug_config():
        """Debug endpoint to check configuration (development only)."""
        return {
            "environment": ENVIRONMENT,
            "debug": DEBUG,
            "database_url": DATABASE_URL.replace(DB_PASSWORD, "***") if DB_PASSWORD else "Not set",
            "url": URL,
            "has_token": bool(TOKEN),
            "channel_id": CHANNEL_ID,
        }

