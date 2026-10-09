# APES-26 Lifecycle & Gates

This is the complete product-engineering control loop. The agent does not blindly execute every item on every task; it selects the applicable gates based on impact.

## 00 — Intake

Capture request, repository context, constraints, affected surfaces and expected outcome.

**Gate:** request is understood; ambiguity that can materially change the result is resolved or explicitly documented as an assumption.

## 01 — Discovery

Identify users, problem, desired outcome, business value, current behavior, constraints, risks and non-goals.

**Artifacts:** `docs/PRODUCT.md`, assumptions.

## 02 — Requirements

Convert the outcome into functional/non-functional requirements and testable acceptance criteria.

**Gate:** every critical requirement has a verification method.

## 03 — Domain & Data Model

Identify entities, ownership, lifecycle, relationships, validation, retention, migrations, tenancy and audit requirements.

**Gate:** destructive or irreversible data changes have a migration/rollback strategy.

## 04 — UX Architecture

Map information architecture, user journeys, screens, states, responsive behavior and accessibility.

**Gate:** primary flow and failure states are explicit.

## 05 — UI / Design System

Define or reuse typography, spacing, color, components, interaction patterns, responsive rules and visual hierarchy.

**Gate:** UI is coherent with the existing system and has all important states.

## 06 — Technical Architecture

Define runtime boundaries, modules, data flow, integrations, AI boundaries, failure modes, observability and deployment model.

**Gate:** architecture is simpler than necessary alternatives and important decisions are recorded.

## 07 — Implementation

Implement in small vertical slices. Keep interfaces typed and validated. Avoid speculative abstractions.

**Gate:** each slice satisfies its acceptance criteria before moving on.

## 08 — Verification

Run static checks, unit/integration/E2E tests and browser verification for UI. Verify edge/error states.

**Gate:** evidence exists for critical paths.

## 09 — Security Hardening

Review authentication, authorization, tenant isolation, input validation, secrets, uploads, webhooks, rate limits, injections, SSRF, XSS/CSRF where applicable, AI prompt injection and tool authorization.

**Gate:** no unresolved critical security issue.

## 10 — Accessibility

Check semantic structure, keyboard access, focus, labels, contrast, reduced motion and screen-reader semantics as applicable.

**Gate:** project target is met or exceptions are documented.

## 11 — Performance

Review loading, rendering, bundle, images, caching, network calls, database queries and Core Web Vitals impact.

**Gate:** no unacceptable regression against project budget.

## 12 — SEO / Discoverability

For public pages: metadata, canonical, sitemap, robots, structured data, Open Graph, semantic HTML and indexability.

**Gate:** public pages are crawlable/indexable as intended.

## 13 — AI Evaluation

For AI features: schema validity, correctness, groundedness, tool-call behavior, refusal/safety, latency, cost and regression cases.

**Gate:** critical evaluation cases pass.

## 14 — Release

Build, migrations, environment configuration, preview/staging checks, smoke tests and rollback path.

**Gate:** production readiness checklist passes.

## 15 — Observability

Monitor errors, latency, uptime, database, external services, AI latency/cost/errors and key product events.

**Gate:** critical failures are detectable.

## 16 — Learning Loop

Use real feedback, analytics, support issues, evaluation regressions and technical metrics to update product and engineering priorities.

**Gate:** learnings become documented decisions or backlog items rather than disappearing into chat history.

## Change-class matrix

### Small UI/content change
Applicable: Intake → Implementation → Verification → Accessibility → Browser.

### Feature
Applicable: Intake → Discovery/Requirements → UX → Architecture → Implementation → Verification → Security → Performance → Browser.

### AI feature
Add: AI Architecture → Evaluation → AI Security → Cost/Latency.

### Database/auth/security change
Mandatory `/plan`, architecture review, migration/rollback and security gate.

### Production release
Full release gates, smoke test and observability check.
