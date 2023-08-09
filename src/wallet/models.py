from sqlalchemy import Column, Integer, Boolean, Float, ForeignKey, CHAR, String
from sqlalchemy_utils import URLType

from src.core.database import Base


class Wallet(Base):
    __tablename__ = 'wallet'
    id = Column(Integer, primary_key=True, unique=True)
    address = Column(String)
    balance = Column(Float)
    private_key = Column(String)

# class Asset(Base):
#     __tablename__ = 'asset'
#     id = Column(Integer, primary_key=True, unique=True)
#     image = Column(URLType)
#     short_name = Column(String)
#     decimal_places = Column(Integer)
#     symbol = Column(String)
