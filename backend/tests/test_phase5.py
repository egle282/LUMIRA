import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app

@pytest.mark.asyncio
async def test_lum_bill_001_billing_upgrade_bypass():
    # Attempting to upgrade without Stripe configuration must fail closed
    # Wait, the endpoint uses get_current_user dependency!
    from backend.api.deps import get_current_user
    from backend.database.models import User
    async def mock_get_current_user():
        return User(id="test_user", tenant_id="tenant_1")
    
    app.dependency_overrides[get_current_user] = mock_get_current_user
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/billing/upgrade", params={"plan_name": "premium"})
        assert response.status_code == 503
        assert "configured" in response.json()["detail"].lower()
        
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
async def test_lum_sec_006_safe_api_errors():
    # Chat endpoint without token normally returns 401, but we mock it or just call it without token.
    # Wait, /api/chat requires get_current_user. Let's mock it to bypass auth and force an error.
    from backend.api.deps import get_current_user
    from backend.database.models import User
    
    async def mock_get_current_user():
        return User(id="test_user", tenant_id="tenant_1")
        
    app.dependency_overrides[get_current_user] = mock_get_current_user
    
    # We will trigger an error by patching orchestrator to fail
    from unittest.mock import patch
    import os
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "fake_key"}):
        with patch("backend.api.chat.AIOrchestrator.interpret_chart") as mock_interpret:
            mock_interpret.side_effect = Exception("Super secret database error: user password hash leaked")
            
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                response = await ac.post("/api/chat", json={"message": "hello"})
                # Chat endpoint handles this by returning a 200 with an error reply (due to its design).
                # But the error message must NOT contain the secret!
                assert response.status_code == 200
                data = response.json()
                assert "внутренняя ошибка" in data["reply"].lower()
                assert "Код ошибки" in data["reply"]
                assert "leaked" not in data["reply"]
                
    app.dependency_overrides.clear()
