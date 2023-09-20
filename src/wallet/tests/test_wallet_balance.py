import pytest


@pytest.mark.asyncio
async def test_wallet_balance(client, auth_user):
    response = await client.post("/api/v1/wallet/balance/", params={
        'wallet_address': '0xD8f38DaA59799900b9629622b8D9B17a3CfD4bA9',
    })
    print(response.json())
    assert response.status_code == 200
