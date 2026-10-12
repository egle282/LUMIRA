from types import SimpleNamespace

import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app
from backend.api.deps import get_current_user, get_db
from backend.core import config


@pytest.mark.asyncio
async def test_checkout_creates_real_provider_session(monkeypatch):
    monkeypatch.setattr(config.settings, "STRIPE_SECRET_KEY", "sk_test_configured")
    monkeypatch.setattr(config.settings, "STRIPE_PRICE_PRO", "price_pro_monthly")
    monkeypatch.setattr(config.settings, "FRONTEND_URL", "https://lumira.example")

    class Scalars:
        def first(self):
            return None

    class Result:
        def scalars(self):
            return Scalars()

    class FakeSession:
        async def execute(self, statement):
            return Result()

    async def current_user():
        return SimpleNamespace(id="user-123", tenant_id="tenant-456", email="user@example.com")

    async def db_session():
        yield FakeSession()

    def fake_create(**kwargs):
        assert kwargs["api_key"] == "sk_test_configured"
        assert kwargs["mode"] == "subscription"
        assert kwargs["line_items"] == [{"price": "price_pro_monthly", "quantity": 1}]
        assert kwargs["metadata"]["user_id"] == "user-123"
        assert kwargs["metadata"]["tenant_id"] == "tenant-456"
        return SimpleNamespace(url="https://checkout.stripe.test/session", id="cs_test_123")

    import backend.api.billing as billing
    monkeypatch.setattr(billing.stripe.checkout.Session, "create", fake_create)
    app.dependency_overrides[get_current_user] = current_user
    app.dependency_overrides[get_db] = db_session
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/billing/upgrade", params={"plan_name": "pro"})
        assert response.status_code == 200
        assert response.json() == {
            "status": "pending",
            "checkout_url": "https://checkout.stripe.test/session",
            "session_id": "cs_test_123",
        }
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_checkout_fails_closed_when_price_is_missing(monkeypatch):
    monkeypatch.setattr(config.settings, "STRIPE_SECRET_KEY", "sk_test_configured")
    monkeypatch.setattr(config.settings, "STRIPE_PRICE_PRO", None)

    class Scalars:
        def first(self):
            return None

    class Result:
        def scalars(self):
            return Scalars()

    class FakeSession:
        async def execute(self, statement):
            return Result()

    async def current_user():
        return SimpleNamespace(id="user-123", tenant_id="tenant-456", email="user@example.com")

    async def db_session():
        yield FakeSession()

    app.dependency_overrides[get_current_user] = current_user
    app.dependency_overrides[get_db] = db_session
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/billing/upgrade", params={"plan_name": "pro"})
        assert response.status_code == 503
        assert "price" in response.json()["detail"].lower()
    finally:
        app.dependency_overrides.clear()
