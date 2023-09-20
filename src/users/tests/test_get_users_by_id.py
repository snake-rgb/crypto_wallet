import pytest


@pytest.mark.asyncio
async def test_get_user_by_id(client, auth_user):
    response = await client.get("/api/v1/get_user_by_id/1")
    print(response.json())
    assert response.status_code == 200
