import datetime
from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy_utils import URLType

from src.core.database import Base


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String)
    image = Column(URLType)
    price = Column(DECIMAL())
    wallet_address = Column(String)


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, unique=True)
    transaction_id = Column(Integer, ForeignKey('transactions.id'))
    # args  =  model name, table name
    transaction = relationship('Transaction', foreign_keys=[transaction_id])

    date = Column(DateTime(), default=datetime.datetime.utcnow())
    status = Column(Enum('NEW', 'DELIVERY', 'SUCCESS', 'FAILED', 'REFUND',
                         name='order_status',
                         create_type=True),
                    default='NEW')
    # 'NEW', 'DELIVERY', 'SUCCESS', 'FAILED', 'REFUND',
    product_id = Column(Integer, ForeignKey('products.id'))
    product = relationship('Product', foreign_keys=[product_id])

    return_transaction_id = Column(Integer, ForeignKey('transactions.id'), nullable=True)
    return_transaction = relationship('Transaction', foreign_keys=[return_transaction_id])
