"""API endpoint tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_readiness_check(client: AsyncClient):
    """Test readiness check endpoint."""
    response = await client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data


@pytest.mark.asyncio
async def test_liveness_check(client: AsyncClient):
    """Test liveness check endpoint."""
    response = await client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"


@pytest.mark.asyncio
async def test_create_call(client: AsyncClient):
    """Test creating a call."""
    response = await client.post(
        "/api/v1/calls/",
        json={
            "phone_number": "+1234567890",
            "language": "en-US",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["phone_number"] == "+1234567890"
    assert data["status"] == "initiated"


@pytest.mark.asyncio
async def test_get_call(client: AsyncClient):
    """Test getting a call."""
    # First create a call
    create_response = await client.post(
        "/api/v1/calls/",
        json={
            "phone_number": "+1234567890",
            "language": "en-US",
        },
    )
    call_id = create_response.json()["id"]

    # Then get it
    response = await client.get(f"/api/v1/calls/{call_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == call_id


@pytest.mark.asyncio
async def test_list_calls(client: AsyncClient):
    """Test listing calls."""
    # Create a few calls
    for i in range(3):
        await client.post(
            "/api/v1/calls/",
            json={
                "phone_number": f"+123456789{i}",
                "language": "en-US",
            },
        )

    # List calls
    response = await client.get("/api/v1/calls/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3

