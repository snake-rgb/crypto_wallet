import pytest


@pytest.mark.asyncio
async def test_wallet_transaction_by_hash(client, auth_user):
    response = await client.post("/api/v1/wallet/transaction/by_hash/", params={
        'transaction_hash': '0xd59e15f1654d5f36bd839e22234c177cc8a64cecda1205909fb43423b5205ee9',
    })
    print(response.json())
    assert response.status_code == 200
