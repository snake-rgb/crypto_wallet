import pytest


@pytest.mark.asyncio
async def test_wallet_get_user_wallets(client, auth_user):
    response = await client.get("/api/v1/wallet/get-user-wallets/")
    print(response.json())
    assert response.status_code == 200
