import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app

@pytest.mark.asyncio
async def test_lum_bill_001_billing_upgrade_bypass():
    # Attempting to upgrade without Stripe configuration must fail closed
    from backend.api.deps import get_current_user, get_db
    from backend.database.models import User

    class EmptyScalars:
        def first(self):
            return None

    class EmptyResult:
        def scalars(self):
            return EmptyScalars()

    class FakeSession:
        async def execute(self, statement):
            return EmptyResult()

    async def mock_get_current_user():
        return User(id="test_user", tenant_id="tenant_1")

    async def mock_get_db():
        yield FakeSession()

    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[get_db] = mock_get_db

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/api/billing/upgrade", params={"plan_name": "premium"})
            assert response.status_code == 503
            assert "configured" in response.json()["detail"].lower()
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_lum_auth_001_registration_validation():
    # Test weak password
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/auth/register", json={
            "email": "test@example.com",
            "password": "weak"
        })
        assert response.status_code == 422 # Pydantic validation error
        
        # Test missing uppercase
        response = await ac.post("/api/auth/register", json={
            "email": "test@example.com",
            "password": "password123"
        })
        assert response.status_code == 422
        
        # Test missing number
        response = await ac.post("/api/auth/register", json={
            "email": "test@example.com",
            "password": "PasswordStrong"
        })
        assert response.status_code == 422
        
        # Test invalid email format
        response = await ac.post("/api/auth/register", json={
            "email": "not-an-email",
            "password": "Password123"
        })
        assert response.status_code == 422

@pytest.mark.asyncio
async def test_chat_requires_birth_profile_without_leaking_internal_details():
    from backend.api.deps import get_current_user
    from backend.database.database import get_db
    from backend.database.models import User

    class EmptyScalars:
        def first(self):
            return None

    class EmptyResult:
        def scalars(self):
            return EmptyScalars()

    class FakeSession:
        async def execute(self, statement):
            return EmptyResult()

    async def mock_get_current_user():
        return User(id="test_user", tenant_id="tenant_1")

    async def mock_get_db():
        yield FakeSession()

    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[get_db] = mock_get_db
    try:
        from unittest.mock import patch
        import os
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                response = await ac.post("/api/chat", json={"message": "hello"})
        assert response.status_code == 400
        assert "профиль рождения" in response.json()["detail"].lower()
        assert "password hash" not in response.text.lower()
    finally:
        app.dependency_overrides.clear()
