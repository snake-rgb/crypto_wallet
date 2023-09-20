import pytest


@pytest.mark.asyncio
async def test_products(client, auth_user):
    response = await client.get("/api/v1/products/")
    print(response.json())
    assert response.status_code == 200
