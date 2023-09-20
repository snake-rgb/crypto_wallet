import pytest


@pytest.mark.asyncio
async def test_create_user(client):
    response = await client.post("/api/v1/register/", json={
        "username": "username_test",
        "email": "user2@user.com",
        "password": "1230123viK",
        "confirm_password": "1230123viK",
    })
    print(response.json())
    assert response.status_code == 200
