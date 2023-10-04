import datetime

import pytz
from sqladmin import ModelView
from sqlalchemy import Column, Integer, Boolean, Float, ForeignKey, CHAR, String, Numeric, DECIMAL, DateTime, Enum, \
    Index
from sqlalchemy.orm import relationship
from sqlalchemy_utils import URLType

from src.core.database import Base
from src.wallet.enums import TransactionStatus


class Wallet(Base):
    __tablename__ = 'wallets'
    id = Column(Integer, primary_key=True, unique=True)
    address = Column(String)
    balance = Column(DECIMAL())
    private_key = Column(String)

    user_id = Column(Integer, ForeignKey('users.id'))
    # args  =  model name, table name
    user = relationship('User', backref="wallets")

    asset_id = Column(Integer, ForeignKey('assets.id'))
    # args  =  model name, table name
    asset = relationship('Asset', backref="wallets")


wallet_address_index = Index('wallet_address_index', Wallet.user_id, Wallet.address, unique=True)


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


class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True, unique=True)
    hash = Column(String, unique=True)
    from_address = Column(String)
    to_address = Column(String)
    value = Column(DECIMAL())
    age = Column(DateTime(), default=datetime.datetime.now())
    fee = Column(DECIMAL())
    status = Column(Enum(TransactionStatus),
                    default=TransactionStatus.PENDING)


class AssetAdmin(ModelView, model=Asset):
    column_list = [Asset.id, Asset.short_name, Asset.symbol, Asset.decimal_places]


class WalletAdmin(ModelView, model=Wallet):
    column_list = [Wallet.id, Wallet.address, Wallet.user, Wallet.asset, Wallet.balance, Wallet.private_key]


class TransactionAdmin(ModelView, model=Transaction):
    column_list = [Transaction.id, Transaction.hash, Transaction.from_address, Transaction.to_address,
                   Transaction.value, Transaction.age, Transaction.fee, Transaction.status]
