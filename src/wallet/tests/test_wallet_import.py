import pytest


@pytest.mark.asyncio
async def test_wallet_import(client, auth_user):
    response = await client.post("/api/v1/wallet/import/", params={
        'private_key': '2f04d9d5ac56bbc7f4f4be109d81f35c94a817994ccd13d7b15e76093bdc332e',
    })
    print(response.json())
    assert response.status_code == 200
