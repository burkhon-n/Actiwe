from sqlalchemy import Column, Integer, BigInteger, Enum
from database import Base

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    telegram_id = Column(BigInteger, nullable=False, unique=True)
    role = Column(Enum('admin', 'sadmin', name='role'), nullable=False)
    broadcasting = Column(Enum('forward', 'copy', name='broadcasting'), nullable=True)
    
    def __init__(self, telegram_id: int, role: str):
        self.telegram_id = telegram_id
        self.role = role

    def __repr__(self):
        return f"<Admin(telegram_id={self.telegram_id}, role={self.role})>"