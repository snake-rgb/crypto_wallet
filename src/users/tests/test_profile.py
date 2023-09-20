import pytest


@pytest.mark.asyncio
async def test_profile(client, auth_user):
    response = await client.get("/api/v1/profile/")
    print(response.json())
    assert response.status_code == 200
