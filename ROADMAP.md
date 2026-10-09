# LUMIRA ROADMAP

Based on `Roade_map.txt` and dependencies.

## Milestone 0: Discovery & Setup (Current)
- [x] Audit project and initialize documentation.
- [ ] Setup repository structure, linters, Docker.
- [ ] Database schema design (Identity, RLS).

## Milestone 1: MVP (Telegram + Core Astrology)
- [ ] **Foundation:** Setup CI/CD, Logging, Database.
- [ ] **Astrology Core:** Integrate Swiss Ephemeris (Chart, Panchanga, Dasha, Transits).
- [ ] **Identity:** Users, Tenants, Profiles (RLS not enforced in backend).
- [ ] **AI Layer:** Provider abstraction, prompts, structured output.
- [x] **AI Astrologer:** Chat context, memory.
- [ ] **Telegram MVP:** Onboarding, Chart, Daily briefing, Muhurta, Chat.

## Milestone 2: V1 (Web + Subscriptions)
- [x] **Web Frontend:** Dashboard, Chart, Predictions, Muhurta (Mock), AI Chat.
- [ ] **Advanced Features:** Memory persistence, Daily Briefing scheduling, Life Areas.
- [ ] **Billing:** Subscriptions (partial), Webhooks (missing), Usage limits (missing).
- [ ] **Admin Panel:** SaaS management, AI Costs, Feature flags.

## Milestone 3: V2 (Advanced Astrology)
- [ ] **Karma Timeline:** Timeline engine.
- [ ] **Destiny Matrix:** Calculation engine and interpretation.
- [ ] **Life Event Engine:** Probabilistic predictions.
- [ ] **Knowledge & Evolution Engine:** Pattern recognition, self-improvement.

## Milestone 4: Production Readiness & CI/CD
- [ ] **Infrastructure Decision:** Choose Cloud Provider (AWS/GCP/DO) and Database Hosting (Managed vs Self-hosted).
- [ ] **Domain & SSL:** Configure Nginx/Caddy with Let's Encrypt for HTTPS.
- [ ] **CI/CD Pipeline Setup:** Finalize GitHub Actions (tests, build, automated deploy).
- [ ] **QA & Security:** E2E, Load Testing, AI Evaluations, Security audit.
- [ ] **Deployment:** Domain setup, Monitoring, Backups, Rollback strategies.
