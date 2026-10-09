# Portable AI Engineering Pack Manifest

Version: 1.2.0
Status: controlled reusable framework
Owner: TODO
Last reviewed: 2026-08-13

## Purpose

This folder is a portable operating framework for AI-assisted software delivery. It combines user context, canonical agent instructions, security controls, production runbooks, compliance checklists, client handover material, observability rules and quality automation.

## Canonical files

| Component | Canonical path | Purpose | Lifecycle |
|---|---|---|---|
| Agent policy | `AGENTS.md` | Highest-priority working rules for the AI agent. | Active |
| User context | `USER.md` | Compact user preferences and collaboration style. | Active |
| Security baseline | `SECURITY.md` | Security, secrets, CI/CD, payments and incident policy. | Active |
| Project facts | `PROJECT_STATUS.md` | Verified stack, environments, commands and owners. | Fill per project |
| Module rules | `Ruls_ReFF.txt` | Modularity and safe refactoring standard. | Active |
| Architecture linter | `reff_linter.py` | Python architecture and size checks. | Active |
| Linter configuration | `.reff-linter.toml` | Project scope, thresholds and reviewed exclusions. | Fill per project |
| Pre-commit | `.pre-commit-config.yaml` | Local quality and secret checks. | Active |
| Production gate | `scripts/check-prelaunch.sh` | Blocks deployment on open P0/P1. | Active |
| Pack smoke test | `scripts/pack-smoke-test.sh` | Validates the pack itself before distribution. | Active |
| Prometheus rules | `config/prometheus/alerts/payments-security.yml` | Payment and API security alerts. | Adapt per project |
| System Design skill | `.claude/skills/system-design-architect/` | Distributed systems, scalability, HLD/LLD, messaging, reliability and AI system design knowledge. | Active |

## Directory lifecycle

`.claude/commands`, `.claude/skills` and `.claude/rules` are reusable content, but only files linked from `AGENTS.md` or the project manifest are canonical for the active workflow. Historical, experimental and vendor material must be marked `legacy` or excluded from active scans.

`docs/production`, `docs/security`, `docs/delivery`, `docs/legal`, `docs/observability` and `docs/runbooks` contain templates. They are not evidence of compliance or production readiness until filled with verified project facts, owners, dates and artifacts.

## Installation contract

1. Copy the pack into a new project without copying secrets, `.env`, credentials, session files or backup directories.
2. Review `AGENTS.md`, `SECURITY.md` and `PROJECT_STATUS.md`.
3. Fill the actual stack and commands in `PROJECT_STATUS.md`.
4. Set the `include` scope in `.reff-linter.toml`.
5. Run `scripts/pack-smoke-test.sh`.
6. Install pre-commit and run it on all files.
7. Run `/prelaunch` before deployment.

## Versioning and change policy

Changes to `AGENTS.md`, `SECURITY.md`, `.claude/settings.json`, `.claude/mcp.json`, `.antigravity/ralph.sh`, `.reff-linter.toml` or smoke-test scripts require review. Each pack release must record version, changed files, security impact, migration notes and test evidence.

## Explicit non-goals

The pack does not itself prove legal compliance, security certification, payment-provider approval, backup recoverability or production readiness. Those claims require project-specific evidence and qualified review.

- Production-grade System Design V2: capacity planning, decision trees, failure engineering, SLOs, AI architecture patterns, case studies and review scorecard.
