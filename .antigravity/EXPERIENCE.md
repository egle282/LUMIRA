# Experience

- Fixed Dashboard.tsx unclosed div error.
- Upgraded Muhurta frontend mock with dynamic data based on activity type, preventing duplicate responses.
- Implemented Glassmorphism UI for form elements (select, input) in Muhurta.tsx.
- Forced AI Chat responses to Russian.
- **Security Audit (2026-10-09):** Never trust documentation claims without auditing the code (RLS, Prompt Injection, Webhooks were claimed but missing/partially implemented).
- **RLS Enforcement:** Always inject RLS context explicitly inside SQLAlchemy sessions during auth (`app.current_tenant` via `set_tenant_context` in `deps.py`).
- **Docker Security:** Protect docker-compose files by binding ports to `127.0.0.1` and adding authentication to backend services (like Redis).
