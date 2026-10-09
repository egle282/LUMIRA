# SECURITY MODEL

## 1. Tenant Isolation
- **Row-Level Security (RLS):** **VERIFIED**. SQL policies exist in `setup_rls.sql`, and `backend/api/deps.py` explicitly injects `app.current_tenant` into the SQLAlchemy session during authentication, enforcing RLS on all subsequent queries.
- **API Boundaries:** **VERIFIED**. `tenant_id` is derived implicitly from the authenticated user.

## 2. Authentication & Authorization
- **Web App:** **VERIFIED**. JWT authentication is enforced via `deps.py` using `OAuth2PasswordBearer`.
- **Telegram Bot:** **NOT VERIFIED**. Basic bot skeleton exists but security mechanisms are undefined.
- **Admin Panel:** **NOT IMPLEMENTED**. No RBAC or `SUPER_ADMIN` logic currently exists in the application.

## 3. Data Privacy (PII)
- Birth data (Date, Time, Location) is sensitive.
- Passwords (if any) hashed with Argon2 or bcrypt (handled by Supabase/Auth provider if used).
- Telemetry/Logs: **PARTIAL**. Basic structlog logging is present in `chat.py`, avoiding explicit PII logging, but no systematic redaction layer is implemented.

## 4. AI Security
- **Prompt Injection:** **NOT IMPLEMENTED**. User inputs are passed directly to the orchestrator (`backend/ai/chat.py`) without sanitization.
- **Data Leakage:** **NOT VERIFIED**. RAG context isolation depends on DB isolation, which is currently not enforced (see section 1).

## 5. Financial Security
- **Webhooks:** **NOT APPLICABLE**. There are currently no webhook endpoints for billing providers in the codebase.
- **Idempotency:** **NOT IMPLEMENTED**. Billing routes (`/upgrade`) lack idempotency keys.
