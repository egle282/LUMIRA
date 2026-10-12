# LUMIRA Security Model and Release Status

This document distinguishes implemented controls from controls that still need deployment-level verification. A passing CI run validates the checks in the workflow; it is not a full independent security audit.

## 1. Tenant isolation (PostgreSQL RLS)

- RLS is enabled and forced on users, profiles, interaction_logs, memories, and subscriptions.
- App queries that touch tenant-scoped tables must call set_tenant_context(session, tenant_id) inside the active transaction before querying or writing.
- Tenant context is derived from the authenticated user's validated JWT for web API requests. Telegram flows first perform read-only Telegram-ID lookup using the dedicated admin connection, then use the application connection with the resolved tenant context for profile access and writes.
- WITH CHECK policies prevent application-role inserts/updates from writing rows for another tenant.
- The dedicated admin connection is intended for read-only cross-tenant reporting and account lookup. It is granted SELECT only by the initializer; it must not be configured with a superuser or BYPASSRLS role.
- Policies permit cross-tenant SELECT for the configured admin role. The initializer substitutes the validated ADMIN_DB_USER identifier into the policy SQL.
- Deployment verification still required: confirm actual PostgreSQL role attributes and grants in the target installation, and test cross-tenant reads/writes using the real app/admin credentials.

## 2. Authentication and authorization

- Web API routes use JWT bearer authentication and derive tenant identity from the signed token rather than an X-Tenant-ID header.
- Registration sets tenant context before inserting the new tenant-scoped user row.
- Cross-tenant email lookup for registration/login uses the read-only admin connection; this connection must remain read-only.
- Admin API authorization checks the authenticated user's role value. A broader role/permission matrix is not implemented.
- Telegram bot identity is the Telegram platform user ID; the bot does not use the web JWT flow.

## 3. Birth data and privacy

- Birth date, time, location, and coordinates are sensitive personal data.
- The Telegram onboarding flow does not fabricate a city geocode. Until a geocoding provider is configured, the user must supply latitude, longitude, and a valid IANA timezone.
- Avoid logging birth data, prompts, passwords, API keys, and tokens. Review exception logging and retention policy before a public production deployment.
- Production must use unique secrets, restricted network exposure, HTTPS via a reverse proxy, and regular database backups.

## 4. AI security and limitations

- User text sent to an LLM is untrusted input. Dedicated prompt-injection defenses and systematic output validation are not implemented.
- Do not treat generated astrological interpretations as medical, legal, financial, or other professional advice.
- Verify provider configuration, data retention, and cross-tenant isolation before sending real users' data to an external model.

## 5. Billing

- Billing upgrade and webhook endpoints return HTTP 501 until a payment provider with signature verification and replay/idempotency protection is implemented. No paid subscription should be activated based on client-side claims.

## 6. Release gate

A stable production release requires:
1. CI green on the exact candidate commit.
2. Successful clean-install development and production Compose smoke tests.
3. RLS tests using actual PostgreSQL app/admin roles, including cross-tenant denial and admin read-only checks.
4. A real Telegram end-to-end test with a valid bot token and database.
5. A deployment-specific review of secrets, HTTPS, backups, rate limiting, logging, and AI provider data policy.
