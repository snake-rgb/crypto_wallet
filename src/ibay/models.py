from sqladmin import ModelView
from sqlalchemy import Column, Integer, String, DECIMAL

from sqlalchemy_utils import URLType
from src.core.database import Base


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String)
    image = Column(URLType)
    price = Column(DECIMAL())
    wallet_address = Column(String)


class ProductAdmin(ModelView, model=Product):
    column_list = [Product.id, Product.price, Product.name, Product.image, Product.wallet_address]
