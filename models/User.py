from sqlalchemy import Column, BigInteger, String, Integer, Boolean
from database import Base
import time

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    language_code = Column(String(10), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(Integer, nullable=False, default=lambda: int(time.time()))
    updated_at = Column(Integer, nullable=True)
    last_interaction = Column(Integer, nullable=True)

    def __init__(self, telegram_id: int, language_code: str = None):
        self.telegram_id = telegram_id
        self.language_code = language_code
        self.created_at = int(time.time())
        self.last_interaction = int(time.time())

    def update_interaction(self):
        """Update the last interaction timestamp"""
        self.last_interaction = int(time.time())
        self.updated_at = int(time.time())
        self.is_active = True

    @classmethod
    def get_by_telegram_id(cls, db, telegram_id: int):
        """Get user by telegram ID"""
        return db.query(cls).filter(cls.telegram_id == telegram_id).first()

    @classmethod
    def create_or_update(cls, db, telegram_id: int, language_code: str = None):
        """Create new user or update existing one"""
        user = cls.get_by_telegram_id(db, telegram_id)
        
        if user:
            # Update existing user
            user.language_code = language_code
            user.update_interaction()
        else:
            # Create new user
            user = cls(
                telegram_id=telegram_id,
                language_code=language_code
            )
            db.add(user)
        
        return user

    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id})>"
