import asyncio

import httpx
from httpx import Response, Limits, ConnectTimeout


class DeliveryService:
    @staticmethod
    async def fetch(url: str, client: httpx.AsyncClient) -> bool:
        try:
            response: Response = await client.get(url)
            return True if response.status_code == 200 else False
        except ConnectTimeout:
            return False

    async def bound_fetch(self, semaphore: asyncio.Semaphore, url: str, client: httpx.AsyncClient) -> bool:
        # Getter function with semaphore.
        async with semaphore:
            return await self.fetch(url, client)

    async def delivery(self, request_count: int, url: str) -> bool:
        tasks = []
        semaphore = asyncio.Semaphore(1000)
        async with httpx.AsyncClient(limits=Limits(max_connections=1000, max_keepalive_connections=1000)) as client:
            for i in range(request_count):
                # pass Semaphore and session to every GET request
                task = asyncio.ensure_future(self.bound_fetch(semaphore, url.format(i), client))
                tasks.append(task)

            responses = asyncio.gather(*tasks)
            result = all(list(await responses))
            return result

    async def run_delivery(self) -> bool:
        return await self.delivery(10000, 'https://www.google.com/search/about/')
