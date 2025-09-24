from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from sqlalchemy.pool import NullPool
from sqlalchemy.exc import DisconnectionError, OperationalError
from typing import Generator
import logging
import time
from config import DB_HOST, DB_NAME, DB_PORT, DB_PASSWORD, DB_USER, ENVIRONMENT

logger = logging.getLogger(__name__)

# Try different PostgreSQL drivers in order of preference
def get_database_url():
    """Get database URL with the best available PostgreSQL driver"""
    base_url = f"{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Try psycopg2 first (most compatible with SQLAlchemy)
    try:
        import psycopg2
        logger.info("Using psycopg2 driver")
        return f"postgresql://{base_url}"
    except ImportError:
        logger.debug("psycopg2 not available")
    
    # Try asyncpg (async driver, good performance)
    try:
        import asyncpg
        logger.info("Using asyncpg driver")
        return f"postgresql+asyncpg://{base_url}"
    except ImportError:
        logger.debug("asyncpg not available")
    
    # Try pg8000 (pure Python, most compatible)
    try:
        import pg8000
        logger.info("Using pg8000 driver")
        return f"postgresql+pg8000://{base_url}"
    except ImportError:
        logger.debug("pg8000 not available")
    
    # Fallback to default (might fail but will show clear error)
    logger.warning("No PostgreSQL driver found, using default connection string")
    return f"postgresql://{base_url}"

DATABASE_URL = get_database_url()
logger.info(f"Using database URL: {DATABASE_URL.split('@')[0]}@***")

# Production-ready engine configuration
engine_kwargs = {
    "echo": ENVIRONMENT == "development",  # Log SQL queries in development
    "pool_pre_ping": True,  # Validate connections before use
    "pool_recycle": 3600,   # Recycle connections after 1 hour
    "pool_size": 10,        # Connection pool size
    "max_overflow": 20,     # Max overflow connections
    "connect_args": {
        "connect_timeout": 10,
        "options": "-c timezone=UTC"
    }
}

# Use NullPool for deployment environments that handle their own pooling
if ENVIRONMENT == "production":
    engine_kwargs["poolclass"] = NullPool
    engine_kwargs.pop("pool_size", None)
    engine_kwargs.pop("max_overflow", None)

try:
    engine = create_engine(DATABASE_URL, **engine_kwargs)
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    raise

# Add connection event listeners for better error handling
@event.listens_for(engine, "connect")
def set_postgresql_settings(dbapi_connection, connection_record):
    """Set database connection parameters."""
    try:
        # PostgreSQL specific settings
        with dbapi_connection.cursor() as cursor:
            cursor.execute("SET timezone TO 'UTC'")
            dbapi_connection.commit()
    except Exception as e:
        logger.warning(f"Failed to set PostgreSQL settings: {e}")

@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Test connection on checkout."""
    try:
        with dbapi_connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception as e:
        logger.warning(f"Connection test failed: {e}")
        # This will cause the connection to be discarded and a new one created
        raise DisconnectionError("Connection test failed")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

class DatabaseSessionManager:
    """Context manager for database sessions with proper error handling."""
    
    def __init__(self):
        self.session = None
    
    def __enter__(self):
        self.session = SessionLocal()
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type:
                logger.error(f"Database session error: {exc_val}")
                self.session.rollback()
            else:
                try:
                    self.session.commit()
                except Exception as e:
                    logger.error(f"Failed to commit session: {e}")
                    self.session.rollback()
                    raise
        finally:
            self.session.close()

def get_db() -> Generator[Session, None, None]:
    """Dependency function to provide a database session per request with retry logic."""
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        db = SessionLocal()
        try:
            # Test the connection
            db.execute(text("SELECT 1"))
            yield db
            return
        except (OperationalError, DisconnectionError) as e:
            logger.warning(f"Database connection attempt {attempt + 1} failed: {e}")
            db.close()
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))
            else:
                logger.error("All database connection attempts failed")
                raise
        except Exception as e:
            logger.error(f"Unexpected database error: {e}")
            db.rollback()
            db.close()
            raise

def test_database_connection() -> bool:
    """Test database connectivity."""
    try:
        with DatabaseSessionManager() as db:
            db.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False
