# models/Item.py

from sqlalchemy import Column, Integer, String, BigInteger, Boolean
from sqlalchemy.orm import Session
from database import Base
import time

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    price = Column(Integer, nullable=False)
    image = Column(String(255), nullable=True)
    sizes = Column(String, nullable=False) # "45, 46, 47, 48, ..."
    gender_neutral = Column(Boolean, default=False)
    description = Column(String(1000), nullable=True)
    category_id = Column(Integer, nullable=True)
    created_at = Column(Integer, nullable=False, default=lambda: int(time.time()))
    updated_at = Column(Integer, nullable=True, onupdate=lambda: int(time.time()))
    created_by = Column(BigInteger, nullable=True)
    updated_by = Column(BigInteger, nullable=True)

    # Note: __init__ should be removed if you want SQLAlchemy to handle it automatically,
    # but for your example, it's fine.
    def __init__(self, title: str, price: int, image: str, sizes:str, description: str, category_id: int, created_by: int, updated_by: int, gender_neutral: bool = False):
        self.title = title
        self.price = price
        self.image = image
        self.sizes = sizes
        self.gender_neutral = gender_neutral
        self.description = description
        self.category_id = category_id
        self.created_by = created_by
        self.updated_by = updated_by

    @staticmethod
    def create(session: Session, title: str, price: int, image: str, sizes:str, description: str, category_id: int, created_by: int, updated_by: int, gender_neutral: bool = False) -> "Item":
        item = Item(
            title=title,
            price=price,
            image=image,
            sizes=sizes,
            description=description,
            category_id=category_id,
            created_by=created_by,
            updated_by=updated_by,
            gender_neutral=gender_neutral
        )
        session.add(item)
        return item

    @staticmethod
    def get_all(session: Session):
        return session.query(Item).all()

    @staticmethod
    def get(session: Session, item_id: int):
        return session.query(Item).filter_by(id=item_id).first()

    @staticmethod
    def update(session: Session, item_id: int, **kwargs):
        item = session.query(Item).filter_by(id=item_id).first()
        if item:
            for key, value in kwargs.items():
                setattr(item, key, value)
            return item
        return None

    @staticmethod
    def delete(session: Session, item_id: int) -> bool:
        item = session.query(Item).filter_by(id=item_id).first()
        if item:
            session.delete(item)
            return True
        return False
    


    def __repr__(self):
        # This will now work correctly because the session is still active
        return f"<Item(id={self.id}, title={self.title}, price={self.price})>"