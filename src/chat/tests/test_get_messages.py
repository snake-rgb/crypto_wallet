import pytest


@pytest.mark.asyncio
async def test_get_messages(client, auth_user):
    response = await client.get("/api/v1/get-messages/")
    print(response.json())
    assert response.status_code == 200
