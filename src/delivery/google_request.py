import asyncio

import httpx
from httpx import Response, Limits, ConnectTimeout


async def fetch(url: str, client: httpx.AsyncClient) -> bool:
    try:
        response: Response = await client.get(url)
        return True if response.status_code == 200 else False
    except ConnectTimeout:
        return False


async def bound_fetch(semaphore: asyncio.Semaphore, url: str, client: httpx.AsyncClient) -> bool:
    # Getter function with semaphore.
    async with semaphore:
        return await fetch(url, client)


async def delivery(request_count: int, url: str) -> bool:
    tasks = []
    semaphore = asyncio.Semaphore(1000)
    async with httpx.AsyncClient(limits=Limits(max_connections=1000, max_keepalive_connections=1000)) as client:
        for i in range(request_count):
            # pass Semaphore and session to every GET request
            task = asyncio.ensure_future(bound_fetch(semaphore, url.format(i), client))
            tasks.append(task)

        responses = asyncio.gather(*tasks)
        result = all(list(await responses))
        print(result)
        return result


async def run_delivery() -> bool:
    return await delivery(300, 'https://www.google.com/search/about/')
