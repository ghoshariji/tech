import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_order_insufficient_stock(client: AsyncClient, admin_headers: dict):
    # Create product with low stock
    prod_resp = await client.post(
        "/api/v1/products",
        json={"name": "Low Stock", "sku": "LOW-001", "price": "10.00", "quantity": 2},
        headers=admin_headers,
    )
    product_id = prod_resp.json()["data"]["id"]

    # Create customer
    cust_resp = await client.post(
        "/api/v1/customers",
        json={"full_name": "John Doe", "email": "john.order@test.com", "phone": "555-0001"},
        headers=admin_headers,
    )
    customer_id = cust_resp.json()["data"]["id"]

    # Try to order more than available
    response = await client.post(
        "/api/v1/orders",
        json={
            "customer_id": customer_id,
            "items": [{"product_id": product_id, "quantity": 10}],
        },
        headers=admin_headers,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_order_success(client: AsyncClient, admin_headers: dict):
    prod_resp = await client.post(
        "/api/v1/products",
        json={"name": "Widget X", "sku": "WX-001", "price": "25.00", "quantity": 50},
        headers=admin_headers,
    )
    product_id = prod_resp.json()["data"]["id"]

    cust_resp = await client.post(
        "/api/v1/customers",
        json={"full_name": "Jane Smith", "email": "jane.order@test.com"},
        headers=admin_headers,
    )
    customer_id = cust_resp.json()["data"]["id"]

    response = await client.post(
        "/api/v1/orders",
        json={
            "customer_id": customer_id,
            "items": [{"product_id": product_id, "quantity": 3}],
        },
        headers=admin_headers,
    )
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["total_amount"] == "75.00"
    assert data["status"] == "PENDING"
