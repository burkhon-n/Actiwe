from sqlalchemy import Column, BigInteger, Integer, DateTime, String
from database import Base, Session
import time

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False)
    item_id = Column(Integer, nullable=False)
    size = Column(String, nullable=False)
    gender = Column(String, nullable=True)  # 'male', 'female' or None for gender_neutral items
    quantity = Column(Integer, nullable=False)
    created_at = Column(Integer, nullable=False, default=lambda: int(time.time()))

    def __init__(self, user_id: int, item_id: int, size: str, quantity: int, gender: str = None):
        self.user_id = user_id
        self.item_id = item_id
        self.size = size
        self.gender = gender
        self.quantity = quantity

    @staticmethod
    def create(session: Session, user_id: int, item_id: int, size: str, quantity: int, gender: str = None) -> "CartItem":
        cart_item = CartItem(
            user_id=user_id,
            item_id=item_id,
            size=size,
            quantity=quantity,
            gender=gender
        )
        session.add(cart_item)
        return cart_item

    @staticmethod
    def get_all(session: Session) -> list["CartItem"]:
        return session.query(CartItem).all()

    @staticmethod
    def get(session: Session, cart_item_id: int) -> "CartItem":
        return session.query(CartItem).filter_by(id=cart_item_id).first()

    @staticmethod
    def get_by_user(session: Session, user_id: int) -> list["CartItem"]:
        return session.query(CartItem).filter_by(user_id=user_id).all()

    @staticmethod
    def get_by_user_and_item(session: Session, user_id: int, item_id: int) -> "CartItem":
        return session.query(CartItem).filter_by(user_id=user_id, item_id=item_id).first()

    @staticmethod
    def update(session: Session, cart_item_id: int, **kwargs) -> "CartItem":
        cart_item = session.query(CartItem).filter_by(id=cart_item_id).first()
        if cart_item:
            for key, value in kwargs.items():
                setattr(cart_item, key, value)
            return cart_item
        return None

    @staticmethod
    def delete(session: Session, cart_item_id: int) -> bool:
        cart_item = session.query(CartItem).filter_by(id=cart_item_id).first()
        if cart_item:
            session.delete(cart_item)
            return True
        return False

    def __repr__(self):
        return f"<CartItem(id={self.id}, user_id={self.user_id}, item_id={self.item_id}, quantity={self.quantity})>"