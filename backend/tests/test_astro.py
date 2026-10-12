import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from backend.api.profile import ProfileCreateUpdate
from pydantic import ValidationError
from backend.main import app
from backend.core.config import settings
from jose import jwt
from datetime import datetime, timedelta

@pytest_asyncio.fixture
async def client(db_session):
    from backend.database.database import get_db
    app.dependency_overrides[get_db] = lambda: db_session
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def user_token_headers(db_session):
    # Create a dummy user
    import uuid
    from backend.database.models import User, Tenant
    from backend.database.tenant import set_tenant_context
    tenant = Tenant(id=str(uuid.uuid4()), name="Test Tenant")
    await set_tenant_context(db_session, tenant.id)
    db_session.add(tenant)
    await db_session.commit()
    await set_tenant_context(db_session, tenant.id)
    
    user = User(tenant_id=tenant.id, email="test@example.com", role="user")
    db_session.add(user)
    await db_session.commit()
    
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode = {"sub": user.id, "role": user.role, "tenant_id": user.tenant_id, "exp": expire}
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}

def test_profile_validation():
    # Valid
    ProfileCreateUpdate(
        name="Test",
        birth_date="1990-01-01",
        birth_time_str="12:00",
        lat=55.75,
        lon=37.61,
        timezone="Europe/Moscow"
    )

    # Invalid Timezone
    with pytest.raises(ValidationError):
        ProfileCreateUpdate(
            name="Test",
            birth_date="1990-01-01",
            birth_time_str="12:00",
            lat=55.75,
            lon=37.61,
            timezone="Invalid/Timezone"
        )
        
    # Invalid Lat
    with pytest.raises(ValidationError):
        ProfileCreateUpdate(
            name="Test",
            birth_date="1990-01-01",
            birth_time_str="12:00",
            lat=95.0,
            lon=37.61,
            timezone="Europe/Moscow"
        )

    # Invalid Lon
    with pytest.raises(ValidationError):
        ProfileCreateUpdate(
            name="Test",
            birth_date="1990-01-01",
            birth_time_str="12:00",
            lat=55.0,
            lon=190.0,
            timezone="Europe/Moscow"
        )

@pytest.mark.asyncio
async def test_chart_missing_profile(client: AsyncClient, user_token_headers):
    # A user without a profile should get 400
    response = await client.get("/api/chart/natal", headers=user_token_headers)
    assert response.status_code == 400
    assert "Профиль не заполнен" in response.json()["detail"]

@pytest.mark.asyncio
async def test_chart_with_profile(client: AsyncClient, user_token_headers):
    # Create profile
    profile_data = {
        "name": "Test",
        "birth_date": "1990-01-01",
        "birth_time_str": "15:00",
        "lat": 55.75,
        "lon": 37.61,
        "timezone": "Europe/Moscow"
    }
    res = await client.post("/api/profile/me", json=profile_data, headers=user_token_headers)
    assert res.status_code == 200
    
    # Get chart
    chart_res = await client.get("/api/chart/natal", headers=user_token_headers)
    assert chart_res.status_code == 200
    
    data = chart_res.json()
    assert "ayanamsa" in data
    assert "planets" in data
    assert "Sun" in data["planets"]


def test_natal_chart_returns_motion_for_rahu_and_ketu():
    from datetime import datetime, timezone
    from backend.astrology.engine import engine

    chart = engine.calculate_natal_chart(
        datetime(1990, 1, 1, 9, 0, tzinfo=timezone.utc),
        lon=37.6173,
        lat=55.7558,
    )
    assert "speed" in chart["positions"]["Rahu"]
    assert "speed" in chart["positions"]["Ketu"]
    assert chart["positions"]["Ketu"]["longitude"] == (
        chart["positions"]["Rahu"]["longitude"] + 180
    ) % 360


@pytest.mark.asyncio
async def test_life_areas_endpoint_uses_saved_profile(client: AsyncClient, user_token_headers):
    profile_data = {
        "name": "Life Areas Test",
        "birth_date": "1990-01-01",
        "birth_time_str": "15:00",
        "lat": 55.75,
        "lon": 37.61,
        "timezone": "Europe/Moscow",
    }
    saved = await client.post(
        "/api/profile/me", json=profile_data, headers=user_token_headers
    )
    assert saved.status_code == 200

    response = await client.get(
        "/api/astrology/life-areas", headers=user_token_headers
    )
    assert response.status_code == 200
    result = response.json()
    assert result["career"]["astrological_factors"]
    assert result["career"]["active_periods"]
    assert result["career"]["active_transits"]
    assert result["generated_at"]
