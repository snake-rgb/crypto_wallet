import datetime

from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy_utils import URLType

from src.core.database import Base


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String)
    image = Column(URLType)
    price = Column(DECIMAL(precision=30, scale=18))
    wallet_address = Column(String)


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, unique=True)
    transaction_id = Column(Integer, ForeignKey('transactions.id'))
    # args  =  model name, table name
    transaction = relationship('Transaction', backref="orders")

    date = Column(DateTime(), default=datetime.datetime.utcnow())
    status = Column(Boolean, default=False)

    # return_transaction_id = Column(Integer, ForeignKey('transactions.id'))
    # # args  =  model name, table name
    # return_transaction = relationship('Transaction', backref="orders")
