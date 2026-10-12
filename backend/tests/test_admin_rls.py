import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text

from backend.main import app
from backend.core.config import settings
from backend.api.deps import get_current_user, get_db
from backend.database.database import get_admin_db
from backend.database.models import User, Tenant

# The test database URL
TEST_DB_URL = "postgresql+asyncpg://lumira:lumira_password@127.0.0.1:5433/lumira_db"
# Admin URL
ADMIN_DB_URL = "postgresql+asyncpg://lumira_admin_role:admin_pass@127.0.0.1:5433/lumira_db"

async def override_get_current_admin():
    return User(id="admin_user_id", tenant_id="tenant_id_1", email="admin@test.com", role="admin")

async def override_get_current_user():
    return User(id="normal_user_id", tenant_id="tenant_id_1", email="user@test.com", role="user")

import pytest_asyncio

@pytest_asyncio.fixture(scope="function")
async def seed_data(setup_db):
    engine = create_async_engine(TEST_DB_URL)
    async with engine.begin() as conn:
        # Insert a tenant and users (bypassing RLS or setting tenant)
        await conn.execute(text("SET app.current_tenant = 'tenant_id_1'"))
        await conn.execute(text("INSERT INTO tenants (id, name) VALUES ('tenant_id_1', 'Tenant 1')"))
        await conn.execute(text("INSERT INTO users (id, tenant_id, role, email) VALUES ('admin_user_id', 'tenant_id_1', 'admin', 'admin@test.com')"))
        await conn.execute(text("INSERT INTO users (id, tenant_id, role, email) VALUES ('normal_user_id', 'tenant_id_1', 'user', 'user@test.com')"))
        await conn.execute(text("INSERT INTO interaction_logs (id, tenant_id, user_id, intent, input_text, output_text, tokens_used) VALUES ('log1', 'tenant_id_1', 'admin_user_id', 'ai_chat', 'i', 'o', 100)"))
        
        await conn.execute(text("SET app.current_tenant = 'tenant_id_2'"))
        await conn.execute(text("INSERT INTO tenants (id, name) VALUES ('tenant_id_2', 'Tenant 2')"))
        await conn.execute(text("INSERT INTO users (id, tenant_id, role, email) VALUES ('other_user_id', 'tenant_id_2', 'user', 'other@test.com')"))
        await conn.execute(text("INSERT INTO interaction_logs (id, tenant_id, user_id, intent, input_text, output_text, tokens_used) VALUES ('log2', 'tenant_id_2', 'other_user_id', 'ai_chat', 'i', 'o', 200)"))

        # Reset role/tenant
        await conn.execute(text("RESET app.current_tenant"))

    await engine.dispose()
    yield

@pytest.mark.asyncio
async def test_admin_endpoints_authorized_real_db(seed_data):
    # Set the admin database URL in settings to the role we created
    old_admin_url = settings.ADMIN_DATABASE_URL
    settings.ADMIN_DATABASE_URL = ADMIN_DB_URL
    
    from backend.database import database
    # Recreate the admin engine manually since settings changed after import
    database.admin_engine = create_async_engine(ADMIN_DB_URL, future=True)
    database.AdminAsyncSessionLocal = async_sessionmaker(bind=database.admin_engine, class_=AsyncSession, expire_on_commit=False)
    
    app.dependency_overrides[get_current_user] = override_get_current_admin
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/admin/metrics/ai-cost")
        assert response.status_code == 200
        assert response.json()["total_ai_messages"] == 2  # Includes both tenants
        assert response.json()["token_usage_tracking"] is False
        assert response.json()["estimated_cost_usd"] is None
        
        response = await ac.get("/api/admin/users")
        assert response.status_code == 200
        # Should see all 3 users
        assert len(response.json()) == 3
        
    app.dependency_overrides.clear()
    settings.ADMIN_DATABASE_URL = old_admin_url

@pytest.mark.asyncio
async def test_admin_role_privileges():
    # Test that the admin role is NOT a superuser and does NOT have bypassrls
    engine = create_async_engine(TEST_DB_URL)
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT rolsuper, rolbypassrls FROM pg_roles WHERE rolname = 'lumira_admin_role'"))
        row = result.fetchone()
        assert not row.rolsuper
        assert not row.rolbypassrls
    await engine.dispose()

@pytest.mark.asyncio
async def test_regular_user_rls(seed_data):
    # Ensure normal app flow is still restricted
    engine = create_async_engine(TEST_DB_URL)
    async with engine.begin() as conn:
        # Simulate app user
        await conn.execute(text("SET ROLE lumira_app"))
        await conn.execute(text("SET app.current_tenant = 'tenant_id_1'"))
        
        result = await conn.execute(text("SELECT COUNT(*) FROM users"))
        count = result.scalar()
        assert count == 2 # Only tenant 1 users (admin_user_id, normal_user_id), not other_user_id

        result = await conn.execute(text("SELECT COUNT(*) FROM tenants"))
        assert result.scalar() == 1  # Tenant registry is isolated as well.
        
        result = await conn.execute(text("SELECT SUM(tokens_used) FROM interaction_logs"))
        tokens = result.scalar()
        assert tokens == 100 # Only log1
        
        # Reset role
        await conn.execute(text("RESET ROLE"))
    await engine.dispose()

@pytest.mark.asyncio
async def test_admin_endpoints_no_db_configured(seed_data):
    # Ensure it returns 503 if ADMIN_DATABASE_URL is not set
    from backend.database import database
    old_admin_session = database.AdminAsyncSessionLocal
    database.AdminAsyncSessionLocal = None
    
    app.dependency_overrides[get_current_user] = override_get_current_admin
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/admin/users")
        assert response.status_code == 503
        
    app.dependency_overrides.clear()
    database.AdminAsyncSessionLocal = old_admin_session
