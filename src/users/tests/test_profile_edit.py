import pytest


@pytest.mark.asyncio
async def test_profile_edit(client, auth_user):
    response = await client.put("/api/v1/profile/edit", json={
        "username": "username_test_edited",
        "password": "1230123viK",
        "confirm_password": "1230123viK",
        "profile_image": ""
    })
    print(response.json())
    assert response.status_code == 200
