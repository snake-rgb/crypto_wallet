import pytest


@pytest.mark.asyncio
async def test_latest_order(client, auth_user):
    response = await client.get("/api/v1/latest-order/")
    print(response.json())
    assert response.status_code == 200
