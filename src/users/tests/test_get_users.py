import pytest


@pytest.mark.asyncio
async def test_get_users(client):
    response = await client.get("/api/v1/get_users/")
    print(response.json())
    assert response.status_code == 200
