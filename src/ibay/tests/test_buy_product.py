import pytest


@pytest.mark.asyncio
async def test_products(client, auth_user):
    pass
    # response = await client.post("/api/v1/buy-product/", json={
    #     'from_address': '0xD8f38DaA59799900b9629622b8D9B17a3CfD4bA9',
    #     'product_id': 1,
    # })
    # print(response.json())
    # assert response.status_code == 200
