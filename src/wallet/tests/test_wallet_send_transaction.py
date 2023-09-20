import pytest


@pytest.mark.asyncio
async def test_wallet_send_transaction(client, auth_user):
    response = await client.post("/api/v1/wallet/send-transaction/", json={
        "from_address": "0x9841b300b8853e47b7265dfF47FD831642e649e0",
        "to_address": "0xD8f38DaA59799900b9629622b8D9B17a3CfD4bA9",
        "amount": 0.00001
    })
    print(response.json())
    assert response.status_code == 200
