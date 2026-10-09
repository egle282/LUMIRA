# SECURITY MODEL

## 1. Tenant Isolation
- **Row-Level Security (RLS):** Implemented at the PostgreSQL level. No data can be accessed without a valid `tenant_id` context.
- **API Boundaries:** All API endpoints must implicitly inject the authenticated user's `tenant_id`.

## 2. Authentication & Authorization
- **Web App:** JWT or session-based authentication (e.g., via Supabase Auth or custom).
- **Telegram Bot:** Secure verification of `telegram_id` linked to the user account.
- **Admin Panel:** Role-Based Access Control (RBAC). Only `SUPER_ADMIN` can access tenant-wide or system-wide data.

## 3. Data Privacy (PII)
- Birth data (Date, Time, Location) is sensitive.
- Passwords (if any) hashed with Argon2 or bcrypt.
- Telemetry/Logs MUST NOT contain sensitive user PII (strip email, birth date, exact coordinates).

## 4. AI Security
- **Prompt Injection:** Sanitize user inputs before passing them to the LLM. 
- **Data Leakage:** Ensure the context passed to the LLM strictly belongs to the requesting user. Do not include cross-user data in RAG or memory retrievals.

## 5. Financial Security
- Webhooks from billing providers (Stripe/Telegram) must be cryptographically verified.
- Idempotency keys used for all payment transactions.
