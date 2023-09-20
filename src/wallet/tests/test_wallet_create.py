import pytest


@pytest.mark.asyncio
async def test_wallet_create(client, auth_user):
    response = await client.post("/api/v1/wallet/create/", params={
        "asset_id": 1,
    })
    print(response.json())
    assert response.status_code == 200
