from types import SimpleNamespace

import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app
from backend.api.deps import get_current_user, get_db
from backend.core import config
from backend.database.models import Subscription


@pytest.mark.asyncio
async def test_billing_portal_returns_frontend_contract(monkeypatch):
    monkeypatch.setattr(config.settings, "STRIPE_SECRET_KEY", "sk_test_example")

    class Scalars:
        def first(self):
            return SimpleNamespace(stripe_customer_id="cus_test")

    class Result:
        def scalars(self):
            return Scalars()

    class FakeSession:
        async def execute(self, statement):
            return Result()

    async def current_user():
        return SimpleNamespace(id="user-1", tenant_id="tenant-1")

    async def db_session():
        yield FakeSession()

    class FakePortalSession:
        url = "https://billing.stripe.test/session"

    def fake_create(**kwargs):
        assert kwargs["customer"] == "cus_test"
        return FakePortalSession()

    import backend.api.billing as billing
    monkeypatch.setattr(billing.stripe.billing_portal.Session, "create", fake_create)
    app.dependency_overrides[get_current_user] = current_user
    app.dependency_overrides[get_db] = db_session
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/billing/portal")
        assert response.status_code == 200
        assert response.json() == {"portal_url": "https://billing.stripe.test/session"}
    finally:
        app.dependency_overrides.clear()
