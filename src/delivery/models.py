import datetime

import pytz
from sqladmin import ModelView
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship

from src.core.database import Base
from src.ibay.enums import OrderStatus


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, unique=True)
    transaction_id = Column(Integer, ForeignKey('transactions.id'))
    # args  =  model name, table name
    transaction = relationship('Transaction', foreign_keys=[transaction_id], backref="orders")

    date = Column(DateTime(), default=datetime.datetime.now())
    status = Column(Enum(OrderStatus),
                    default=OrderStatus.NEW)
    product_id = Column(Integer, ForeignKey('products.id'))
    product = relationship('Product', foreign_keys=[product_id], backref="orders")

    return_transaction_id = Column(Integer, ForeignKey('transactions.id'), nullable=True)
    return_transaction = relationship('Transaction', foreign_keys=[return_transaction_id])

    customer_id = Column(Integer, ForeignKey('users.id'))
    customer = relationship('User', backref='orders')


class OrderAdmin(ModelView, model=Order):
    column_list = [Order.id, Order.transaction, Order.date, Order.status, Order.product, Order.return_transaction,
                   Order.customer]
