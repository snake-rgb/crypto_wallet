import pytest


@pytest.mark.asyncio
async def test_token_verify(client, auth_user):
    response = await client.get("/api/v1/token_verify/")
    print(response.json())
    assert response.status_code == 200
