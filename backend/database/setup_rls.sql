-- LUMIRA RLS (Row-Level Security) Setup

-- 1. Enable RLS on tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- 2. Create policies for USERS table
-- Allow users to read/write only if the session's tenant_id matches the row's tenant_id
CREATE POLICY tenant_isolation_users_policy ON users
    USING (tenant_id::text = current_setting('app.current_tenant', TRUE));

-- 3. Create policies for PROFILES table
CREATE POLICY tenant_isolation_profiles_policy ON profiles
    USING (tenant_id::text = current_setting('app.current_tenant', TRUE));

-- 4. Create an admin bypass or service role bypass if necessary
-- Example: A superuser or specific service role can bypass RLS automatically.
-- To force RLS even for table owners:
ALTER TABLE users FORCE ROW LEVEL SECURITY;
ALTER TABLE profiles FORCE ROW LEVEL SECURITY;

/*
Usage in SQLAlchemy (Async):
async with AsyncSessionLocal() as session:
    await session.execute(text("SELECT set_config('app.current_tenant', :tenant_id, false)"), {"tenant_id": current_tenant_id})
    # Now all subsequent queries in this transaction will be isolated to current_tenant_id
*/
