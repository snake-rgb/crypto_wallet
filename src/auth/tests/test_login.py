import pytest


@pytest.mark.asyncio
async def test_login(client):
    response = await client.post("/api/v1/login/", json={
        "email": "user@user.com",
        "password": "1230123viK",
        "remember_me": False
    })
    print(response.json())
    assert response.status_code == 200
