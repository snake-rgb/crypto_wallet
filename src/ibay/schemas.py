from typing import Optional

from pydantic import BaseModel


class ProductSchema(BaseModel):
    name: str
    image: str
    price: float
    wallet_address: str


class OrderSchema(BaseModel):
    transaction_id: int
    return_transaction_id: Optional[int] = None
    product_id: int
    status: str
