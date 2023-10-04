from pydantic import BaseModel


class ProductSchema(BaseModel):
    name: str
    image: str
    price: float
    wallet_address: str


class OrderSchema(BaseModel):
    from_address: str
    product_id: int
