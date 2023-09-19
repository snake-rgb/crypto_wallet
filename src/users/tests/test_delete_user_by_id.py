import pytest


@pytest.mark.asyncio
async def test_delete_user_by_id(client):
    login = await client.post('/api/v1/login/', json={
        'email': 'user@user.com',
        'password': '1230123viK',
        'remember_me': 'true'
    })
    print(login.json())
    response = await client.delete("/api/v1/delete_user_by_id/{user_id}", params={
        "user_id": 1,
    })
    print(response.json())
    assert response.status_code == 200
