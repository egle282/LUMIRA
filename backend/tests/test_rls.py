import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text
from backend.database.models import User, Tenant
from backend.database.tenant import set_tenant_context

@pytest.mark.asyncio
async def test_rls_tenant_isolation(db_session: AsyncSession):
    # 1. Create two tenants
    tenant1 = Tenant(name="Tenant 1")
    tenant2 = Tenant(name="Tenant 2")
    db_session.add(tenant1)
    db_session.add(tenant2)
    await db_session.commit()

    # 2. Create users in each tenant
    async with db_session.begin():
        await set_tenant_context(db_session, tenant1.id)
        user1 = User(tenant_id=tenant1.id, email="user1@example.com", role="user", hashed_password="pw")
        db_session.add(user1)

    async with db_session.begin():
        await set_tenant_context(db_session, tenant2.id)
        user2 = User(tenant_id=tenant2.id, email="user2@example.com", role="user", hashed_password="pw")
        db_session.add(user2)

    # 3. Test isolation for Tenant 1
    async with db_session.begin():
        await set_tenant_context(db_session, tenant1.id)
        result1 = await db_session.execute(select(User))
        users1 = result1.scalars().all()
        assert len(users1) == 1
        assert users1[0].email == "user1@example.com"

    # 4. Test isolation for Tenant 2
    async with db_session.begin():
        await set_tenant_context(db_session, tenant2.id)
        result2 = await db_session.execute(select(User))
        users2 = result2.scalars().all()
        assert len(users2) == 1
        assert users2[0].email == "user2@example.com"

    # 5. Test with no context
    async with db_session.begin():
        await db_session.execute(text("SELECT set_config('app.current_tenant', '', true)"))
        result_none = await db_session.execute(select(User))
        users_none = result_none.scalars().all()
        assert len(users_none) == 0, f"Expected 0 users without context, got {len(users_none)}"


@pytest.mark.asyncio
async def test_rls_tenant_mutations(db_session: AsyncSession):
    import sqlalchemy.exc
    # 1. Create two tenants
    tenant1 = Tenant(name="Tenant A")
    tenant2 = Tenant(name="Tenant B")
    db_session.add(tenant1)
    db_session.add(tenant2)
    await db_session.commit()

    # 2. Add user to Tenant A
    async with db_session.begin():
        await set_tenant_context(db_session, tenant1.id)
        user_a = User(tenant_id=tenant1.id, email="a@example.com", role="user", hashed_password="pw")
        db_session.add(user_a)
        await db_session.flush()
        user_a_id = user_a.id

    # 3. Add user to Tenant B
    async with db_session.begin():
        await set_tenant_context(db_session, tenant2.id)
        user_b = User(tenant_id=tenant2.id, email="b@example.com", role="user", hashed_password="pw")
        db_session.add(user_b)
        await db_session.flush()
        user_b_id = user_b.id

    # 4. Attempt to UPDATE Tenant B user while in Tenant A context
    async with db_session.begin():
        await set_tenant_context(db_session, tenant1.id)
        # SQLAlchemy ORM updates usually fetch first, so lets do an execute update
        result = await db_session.execute(text("UPDATE users SET email = 'hacked@example.com' WHERE id = :uid"), {"uid": user_b_id})
        # The update should affect 0 rows because of RLS
        assert result.rowcount == 0

    # 5. Attempt to INSERT a user with Tenant B id while in Tenant A context
    async with db_session.begin():
        await set_tenant_context(db_session, tenant1.id)
        try:
            # We bypass ORM so we can force the insert without session caching issues
            await db_session.execute(text("INSERT INTO users (id, tenant_id, email, role, hashed_password) VALUES (gen_random_uuid(), :tid, 'new@example.com', 'user', 'pw')"), {"tid": tenant2.id})
            assert False, "Should have raised an exception"
        except sqlalchemy.exc.ProgrammingError as e:
            # PostgreSQL raises an error for WITH CHECK violations
            assert "violates row-level security policy" in str(e)
            
    # 6. Verify Tenant B user is untouched
    async with db_session.begin():
        await set_tenant_context(db_session, tenant2.id)
        result = await db_session.execute(text("SELECT email FROM users WHERE id = :uid"), {"uid": user_b_id})
        email = result.scalar()
        assert email == "b@example.com"
