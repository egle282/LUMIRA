-- LUMIRA tenant isolation policies.
-- Safe to re-apply: policies are dropped and recreated deterministically.

ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenants FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation_tenants_policy ON tenants;
DROP POLICY IF EXISTS tenant_select_policy ON tenants;
DROP POLICY IF EXISTS tenant_insert_policy ON tenants;
DROP POLICY IF EXISTS tenant_update_policy ON tenants;
DROP POLICY IF EXISTS tenant_delete_policy ON tenants;
CREATE POLICY tenant_select_policy ON tenants FOR SELECT
  USING (id::text = current_setting('app.current_tenant', TRUE) OR current_user = 'lumira_admin_role');
CREATE POLICY tenant_insert_policy ON tenants FOR INSERT
  WITH CHECK (TRUE);
CREATE POLICY tenant_update_policy ON tenants FOR UPDATE
  USING (id::text = current_setting('app.current_tenant', TRUE) OR current_user = 'lumira_admin_role')
  WITH CHECK (id::text = current_setting('app.current_tenant', TRUE) OR current_user = 'lumira_admin_role');
CREATE POLICY tenant_delete_policy ON tenants FOR DELETE
  USING (id::text = current_setting('app.current_tenant', TRUE) OR current_user = 'lumira_admin_role');

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE interaction_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE memories ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

ALTER TABLE users FORCE ROW LEVEL SECURITY;
ALTER TABLE profiles FORCE ROW LEVEL SECURITY;
ALTER TABLE interaction_logs FORCE ROW LEVEL SECURITY;
ALTER TABLE memories FORCE ROW LEVEL SECURITY;
ALTER TABLE subscriptions FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS tenant_isolation_users_policy ON users;
CREATE POLICY tenant_isolation_users_policy ON users
  USING (tenant_id::text = current_setting('app.current_tenant', TRUE) OR current_user = 'lumira_admin_role')
  WITH CHECK (tenant_id::text = current_setting('app.current_tenant', TRUE));

DROP POLICY IF EXISTS tenant_isolation_profiles_policy ON profiles;
CREATE POLICY tenant_isolation_profiles_policy ON profiles
  USING (tenant_id::text = current_setting('app.current_tenant', TRUE) OR current_user = 'lumira_admin_role')
  WITH CHECK (tenant_id::text = current_setting('app.current_tenant', TRUE));

DROP POLICY IF EXISTS tenant_isolation_logs_policy ON interaction_logs;
CREATE POLICY tenant_isolation_logs_policy ON interaction_logs
  USING (tenant_id::text = current_setting('app.current_tenant', TRUE) OR current_user = 'lumira_admin_role')
  WITH CHECK (tenant_id::text = current_setting('app.current_tenant', TRUE));

DROP POLICY IF EXISTS tenant_isolation_memories_policy ON memories;
CREATE POLICY tenant_isolation_memories_policy ON memories
  USING (tenant_id::text = current_setting('app.current_tenant', TRUE) OR current_user = 'lumira_admin_role')
  WITH CHECK (tenant_id::text = current_setting('app.current_tenant', TRUE));

DROP POLICY IF EXISTS tenant_isolation_subscriptions_policy ON subscriptions;
CREATE POLICY tenant_isolation_subscriptions_policy ON subscriptions
  USING (tenant_id::text = current_setting('app.current_tenant', TRUE) OR current_user = 'lumira_admin_role')
  WITH CHECK (tenant_id::text = current_setting('app.current_tenant', TRUE));
