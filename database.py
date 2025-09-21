from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from config import DB_HOST, DB_NAME, DB_PORT, DB_PASSWORD, DB_USER
from typing import Generator

# Use the credentials from config.py to create a connection string
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """Dependency function to provide a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
