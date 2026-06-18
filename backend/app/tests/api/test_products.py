import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_product(client: AsyncClient, admin_headers: dict):
    response = await client.post(
        "/api/v1/products",
        json={
            "name": "Test Widget",
            "sku": "WIDGET-001",
            "price": "29.99",
            "quantity": 100,
            "reorder_level": 10,
            "category": "Widgets",
        },
        headers=admin_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["sku"] == "WIDGET-001"


@pytest.mark.asyncio
async def test_create_product_duplicate_sku(client: AsyncClient, admin_headers: dict):
    await client.post(
        "/api/v1/products",
        json={"name": "A", "sku": "DUP-001", "price": "10.00", "quantity": 5},
        headers=admin_headers,
    )
    response = await client.post(
        "/api/v1/products",
        json={"name": "B", "sku": "DUP-001", "price": "10.00", "quantity": 5},
        headers=admin_headers,
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_list_products(client: AsyncClient, admin_headers: dict):
    response = await client.get("/api/v1/products", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_get_product_not_found(client: AsyncClient, admin_headers: dict):
    response = await client.get(
        "/api/v1/products/00000000-0000-0000-0000-000000000000",
        headers=admin_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_product_negative_price(client: AsyncClient, admin_headers: dict):
    response = await client.post(
        "/api/v1/products",
        json={"name": "Bad", "sku": "BAD-001", "price": "-5.00", "quantity": 5},
        headers=admin_headers,
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_unauthenticated_access(client: AsyncClient):
    response = await client.get("/api/v1/products")
    assert response.status_code == 401
