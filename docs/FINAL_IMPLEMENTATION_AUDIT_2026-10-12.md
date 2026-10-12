# LUMIRA — implementation readiness report

**Updated:** 12 October 2026  
**Repository:** https://github.com/egle282/LUMIRA  
**Verified code commit:** `b92d58f3f7a1db74935ef6977af71e1f4efb3d52`  
**Status:** **Self-hosted MVP: READY FOR TEST / LIMITED USE. Full production SaaS: NOT YET.**

This report supersedes earlier audit notes. It reflects the code currently on `main` and the successful GitHub Actions run for the verified commit above. A later commit adds an additional life-areas API test and is being validated separately.

## What is implemented

- Docker Compose development and production configurations, with PostgreSQL, Redis, backend and frontend.
- Registration/login with JWT, profile management and server-side validation of birth date, time, coordinates and IANA timezone.
- Swiss Ephemeris natal chart positions in the Lahiri sidereal zodiac, including Rahu/Ketu, nakshatra/pada, basic Panchanga and local-weekday handling.
- Life-area signals calculated from the saved birth profile, whole-sign houses, current planetary positions and Vimshottari Mahadasha. This is an astrology-oriented interpretation, not a guarantee or professional advice.
- Daily briefing with deterministic data and optional AI interpretation; Gemini fallback is used when configured OpenRouter generation fails.
- Telegram bot onboarding, natal chart, daily briefing and AI chat. A live Telegram conversation still requires a real bot token and has not been independently tested here.
- Stripe Checkout, signed webhook verification, subscription state handling and customer portal. Real payments require Stripe credentials, configured recurring Price IDs and a deployed webhook endpoint.
- Tenant-context RLS on user data and tenant registry; application role is separated from the bootstrap and read-only admin roles.
- Regression tests for profile validation, life-area calculation, billing fail-closed behavior, astrology fields and tenant isolation.

## CI verification

For commit `ba72fb7f9a6d155f6e63e0cf75aeb8cd473c4c79`, GitHub Actions reported:

| Check | Result |
|---|---|
| Backend tests and compile check | PASS |
| Frontend build and typecheck | PASS |
| Docker Compose clean-install smoke test | PASS |
| Production Compose initialization, API proxy and frontend smoke test | PASS |

CI does not validate secrets or third-party accounts supplied by an individual operator. The verified code commit passed all three configured GitHub Actions jobs.

## Explicit limitations

1. **Muhurta:** the UI and API provide an hourly Panchanga screening heuristic. This is not a complete classical election: sunrise/sunset, Rahu-kala, interval-specific lagna, tradition settings and a broader set of doshas are not implemented.
2. **Telegram Stars:** in-app subscription payments are not implemented. Web billing uses Stripe only.
3. **Astrology depth:** life-area readings use whole-sign houses and basic Mahadasha. House-lord strength, divisional charts and a full classical predictive system are not claimed as complete.
4. **Geocoding:** Telegram onboarding asks the user to supply coordinates and an IANA timezone after entering a city; automatic geocoding is not implemented.
5. **External integration tests:** real Stripe checkout/webhooks and a live Telegram bot were not exercised with operator-owned credentials. CI uses test doubles for payment provider behavior.
6. **Production operations:** before exposing a deployment publicly, configure HTTPS/reverse proxy, backups and restore testing, monitoring/alerting, log retention, and provider secrets. Review the database threat model before claiming resistance to arbitrary SQL execution; RLS context is set by the trusted backend.
7. **Migrations:** `create_all` initializes new tables but is not a replacement for a reviewed Alembic migration process when evolving existing production schemas.

## Readiness decision

LUMIRA can be described accurately as a **working self-hosted MVP** for profile-based astrology, AI-assisted chat/briefings, preliminary Panchanga screening, and optional Stripe billing. It should not be marketed as a complete classical Jyotish platform or a fully production-hardened SaaS until the limitations above are addressed and the live integrations are tested in a configured deployment.

## Recommended acceptance checklist

- [ ] Latest `main` CI is green after the newest commit.
- [ ] A clean machine can copy `.env.example`, set unique secrets, and run both Compose modes.
- [ ] An operator verifies signup/login, profile save, natal chart, life areas, briefing, and Muhurta in a browser.
- [ ] An operator tests Telegram onboarding and AI responses with a real bot token and provider key.
- [ ] If charging customers, an operator tests Stripe test-mode checkout, webhook retries, cancellation/portal, and subscription expiry.
- [ ] Backups are restored in a rehearsal; HTTPS, monitoring and alerting are enabled before public production use.
