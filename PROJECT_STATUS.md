# PROJECT STATUS

## WHAT EXISTS
- Project root initialized.
- AI OS `.antigravity/` core is present.
- Frontend (React + Vite): Dashboard, MyChart, AI Chat (integrated), Muhurta (dynamic mock).
- Backend (FastAPI): Auth, Chart generation (Swiss Ephemeris), AI Chat Orchestrator (Prompt engineering updated).
- Database: PostgreSQL (SQLAlchemy models mapped).

## WHAT IS MISSING

- Real Backend Muhurta calculation endpoint (currently a frontend mock).
- Production Cloud Deployment.
- E2E CI/CD pipeline integration.

## WHAT CAN BE REUSED

- `.antigravity` task execution and agent router runtime.
- Existing knowledge bases and prompt setups from the directories.

## WHAT MUST BE REBUILT / BUILT

- **Admin Panel:** Subscription logic and admin control panel.

## WHAT IS RISKY
- **AI Hallucinations:** Risk of LLM doing astrological calculations instead of using the deterministic engine.
- **Multi-tenant Data Leaks:** Strict RLS enforcement is required to prevent data leakage between tenants.
- **Timezone/Location Complexity:** Critical for accurate Panchanga and Muhurta calculations.

## WHAT IS UNKNOWN
- Target Cloud Deployment Provider (AWS, GCP, etc.).
- Chosen Billing Provider (Stripe, Telegram Payments, etc.).
- Choice of primary LLM Provider (Gemini vs OpenRouter etc.) for production, though Gemini is mentioned.
