from typing import Iterator

from pydantic import BaseModel


class AssetSchema(BaseModel):
    image: str
    short_name: str
    decimal_places: int
    symbol: str



