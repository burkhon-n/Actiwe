from sqlalchemy import Column, Integer, BigInteger, DateTime, String
from database import Base, Session
import time

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False)
    user_name = Column(String(100), nullable=True)
    user_phone = Column(String(20), nullable=True)
    location = Column(String(255), nullable=True)
    items = Column(String(1000), nullable=False)  # JSON string of items [item_id: amount, ...]
    created_at = Column(Integer, nullable=False, default=lambda: int(time.time()))

    def __init__(self, user_id: int, items: str, user_name: str = None, user_phone: str = None, location: str = None):
        self.user_id = user_id
        self.items = items
        self.user_name = user_name
        self.user_phone = user_phone
        self.location = location
        self.created_at = int(time.time())