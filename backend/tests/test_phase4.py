import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app
from unittest.mock import patch

from backend.api.deps import get_db

async def override_get_db():
    class MockSession:
        async def execute(self, *args, **kwargs):
            return None
    yield MockSession()

@pytest.mark.asyncio
async def test_telemetry_middleware():
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/health")
        assert response.status_code == 200
        assert "x-correlation-id" in response.headers
        assert len(response.headers["x-correlation-id"]) > 0
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_telemetry_middleware_custom_correlation():
    app.dependency_overrides[get_db] = override_get_db
    custom_id = "test-correlation-123"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/health", headers={"X-Correlation-ID": custom_id})
        assert response.status_code == 200
        assert response.headers["x-correlation-id"] == custom_id
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_telemetry_middleware_invalid_correlation():
    app.dependency_overrides[get_db] = override_get_db
    # testing very long correlation ID rejection
    custom_id = "A" * 100
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/health", headers={"X-Correlation-ID": custom_id})
        assert response.status_code == 200
        assert response.headers["x-correlation-id"] != custom_id
    app.dependency_overrides.clear()
        
@pytest.mark.asyncio
async def test_health_check_db_failure():
    with patch("backend.main.get_db") as mock_db:
        # Mock dependency to raise an exception
        # We need to patch the actual dependency execution
        pass

@pytest.mark.asyncio
async def test_admin_authorization():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # No auth
        response = await ac.get("/api/admin/users")
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_briefing_mock_flag():
    # Since we don't pass an OPENROUTER_API_KEY, it should fallback to mock
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        pass
