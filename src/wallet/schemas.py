import decimal
from typing import Iterator

from pydantic import BaseModel


class AssetSchema(BaseModel):
    image: str
    short_name: str
    decimal_places: int
    symbol: str


class WalletSchema(BaseModel):
    id: int
    address: str
    balance: decimal.Decimal
    asset_image: str


class TransactionSchema(BaseModel):
    from_address: str
    to_address: str
    amount: float
