-- LUMIRA RLS (Row-Level Security) Setup

-- 1. Enable RLS on tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE interaction_logs ENABLE ROW LEVEL SECURITY;

-- 2. Create policies for USERS table
-- Allow users to read/write only if the session's tenant_id matches the row's tenant_id
CREATE POLICY tenant_isolation_users_policy ON users
    USING (tenant_id::text = current_setting('app.current_tenant', TRUE) OR current_user = 'lumira_admin_role');

-- 3. Create policies for PROFILES table
CREATE POLICY tenant_isolation_profiles_policy ON profiles
    USING (tenant_id::text = current_setting('app.current_tenant', TRUE) OR current_user = 'lumira_admin_role');

-- Create policies for INTERACTION_LOGS table
CREATE POLICY tenant_isolation_logs_policy ON interaction_logs
    USING (tenant_id::text = current_setting('app.current_tenant', TRUE) OR current_user = 'lumira_admin_role');

-- 4. Create an admin bypass or service role bypass if necessary
-- Example: A superuser or specific service role can bypass RLS automatically.
-- To force RLS even for table owners:
ALTER TABLE users FORCE ROW LEVEL SECURITY;
ALTER TABLE profiles FORCE ROW LEVEL SECURITY;
ALTER TABLE interaction_logs FORCE ROW LEVEL SECURITY;
