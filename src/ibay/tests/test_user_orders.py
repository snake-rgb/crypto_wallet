import pytest


@pytest.mark.asyncio
async def test_user_orders(client, auth_user):
    response = await client.get("/api/v1/user-orders/")
    print(response.json())
    assert response.status_code == 200
