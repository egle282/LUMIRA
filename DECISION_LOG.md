# DECISION LOG

| Date | Decision | Context | Status |
|---|---|---|---|
| 2026-09-24 | Start Phase 0 Discovery | Initializing project based on MASTER BUILD PROMPT.md requirements. | **Approved** |
| 2026-09-24 | Strict separation of AI and Calculations | The LLM will only interpret data; it will never perform astronomical/astrological calculations. | **Approved** |
| 2026-09-24 | Multi-tenant RLS Database | Using PostgreSQL Row-Level Security for tenant isolation. | **Proposed** |
| 2026-09-24 | Python backend | Given the need for robust AI orchestration and Swiss Ephemeris (`pyswisseph`), Python is the logical choice for the core backend. | **Proposed** |
