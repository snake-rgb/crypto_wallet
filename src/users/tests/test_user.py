import logging
import pytest

logging.basicConfig(level=logging.INFO)


@pytest.mark.asyncio
async def test_home(client):
    response = await client.get("/api/v1/get_users/")
    print(response.text)
    assert response.status_code == 200
