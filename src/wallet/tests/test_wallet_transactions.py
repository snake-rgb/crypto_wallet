import pytest


@pytest.mark.asyncio
async def test_wallet_create(client, auth_user):
    response = await client.get("/api/v1/wallet/transactions/", params={
        'address': '0xD8f38DaA59799900b9629622b8D9B17a3CfD4bA9',
        "limit": 10,
    })
    print(response.json())
    assert response.status_code == 200
