from sqlalchemy import Column, Integer, String, BigInteger, Enum
from database import Base

class ShopTheme(Base):
    __tablename__ = "shop_themes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=True)
    logo = Column(String(255), nullable=False)

    def __init__(self, name: str, logo: str):
        self.name = name
        self.logo = logo

    @staticmethod
    def get_theme(session):
        return session.query(ShopTheme).first()