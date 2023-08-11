from sqlalchemy import Column, Integer, Boolean, Float, ForeignKey, CHAR, String
from sqlalchemy.orm import relationship
from sqlalchemy_utils import URLType

from src.core.database import Base


class Wallet(Base):
    __tablename__ = 'wallets'
    id = Column(Integer, primary_key=True, unique=True)
    address = Column(String)
    balance = Column(Float)
    private_key = Column(String)

    user_id = Column(Integer, ForeignKey('users.id'))
    # args  =  model name, table name
    user = relationship('User', backref="wallets")

    asset_id = Column(Integer, ForeignKey('assets.id'))
    # args  =  model name, table name
    asset = relationship('Asset', backref="wallets")


class Asset(Base):
    __tablename__ = 'assets'
    id = Column(Integer, primary_key=True, unique=True)
    image = Column(URLType)
    short_name = Column(String)
    decimal_places = Column(Integer)
    symbol = Column(String)


class Blockchain(Base):
    __tablename__ = 'blockchains'
    id = Column(Integer, primary_key=True, unique=True)
    image = Column(URLType)
    name = Column(String)
    code = Column(String)
    symbol = Column(String)
    asset_id = Column(Integer, ForeignKey('assets.id'))
    # args  =  model name, table name
    asset = relationship('Asset', backref="blockchains")
