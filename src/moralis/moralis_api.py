import httpx
from fastapi import HTTPException
from propan import RabbitBroker

from config import settings


class MoralisAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def get_native_transactions(self, address: str, limit: int, cursor: str, page: int) -> dict:
        url = f'https://deep-index.moralis.io/api/v2.2/{address}?chain=sepolia'
        if limit:
            url += f'&limit={limit}'

        if cursor:
            url += f'&cursor={cursor}'
        headers = {
            "X-API-Key": self.api_key
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                print("Ошибка при запросе к Moralis API:", response.status_code)
                raise HTTPException(status_code=response.status_code,
                                    detail=f'Api error {response.status_code} - {response.json()}')
