import pytest


@pytest.mark.asyncio
async def test_create_message(client, auth_user):
    response = await client.post("/api/v1/create-message/", json={
        "text": "user@user.com",
        "image": "",
    })
    print(response.json())
    assert response.status_code == 200
