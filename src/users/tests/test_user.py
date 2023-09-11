import logging
import pytest


logging.basicConfig(level=logging.INFO)


@pytest.mark.asyncio
async def test_home(client):
    print("Testing")
    response = await client.get("/get_users/")
    assert response.status_code == 200
    # assert response.text == "Hello, world!"
    print("OK")
