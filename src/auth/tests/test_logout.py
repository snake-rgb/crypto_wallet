import pytest


@pytest.mark.asyncio
async def test_logout(client, auth_user):
    response = await client.get("/api/v1/logout/")
    print(response.json())
    assert response.status_code == 200
