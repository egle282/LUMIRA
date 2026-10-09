# APES-26 — AI Product Engineering System 2026 + Project Factory

A production-grade master template for Google Antigravity 2.x / Antigravity CLI and AI-assisted product engineering.

## What this is

APES-26 is a reusable project operating system. It combines:

- persistent Rules for invariants and constraints
- Agent Skills for repeatable multi-step expertise
- custom subagents for specialist work
- `/plan` for reviewable implementation planning
- product, UX, architecture, AI, security, testing and release artifacts
- quality gates and evidence-based completion
- project profiles for SaaS, AI SaaS, dashboard, landing, bot, API and internal tools

## Lifecycle

`DISCOVER → SPECIFY → MODEL → UX → DESIGN → ARCHITECT → BUILD → VERIFY → HARDEN → RELEASE → OBSERVE → LEARN`

All phases are represented in `docs/LIFECYCLE.md`. They are not a tutorial to follow manually; they are the project's control system. The agent should select the applicable gates automatically.

## Core files

- `AGENTS.md` — top-level operating contract
- `PROJECT.yaml` — project metadata and policy
- `.agents/rules/` — persistent constraints
- `.agents/skills/` — reusable capabilities
- `.agents/agents/` — specialist subagents
- `docs/` — source-of-truth product/engineering artifacts
- `templates/` — repeatable artifact templates
- `config/` — project policy/configuration
- `scripts/` — local validation helpers

## Start

1. Copy the template into a new repository.
2. Fill `PROJECT.yaml` and `docs/PRODUCT.md`.
3. Run `/plan` for the first non-trivial task.
4. Let Antigravity inspect the repository before changing architecture.
5. Use skills/subagents selectively.
6. Require evidence before marking milestones complete.

## Technology policy

APES-26 is stack-agnostic. Do not hard-code a framework merely because the template mentions it. Pin versions from the actual project lockfile and verify current official documentation before upgrades.

## Compatibility note

The template uses `.agents/rules`, `.agents/skills` and `.agents/agents`, matching current Antigravity discovery conventions. Legacy Workflows are intentionally omitted; Google documents their migration to Agent Skills and retirement on November 1, 2026.


## Project Factory

The repository now includes a first-class Project Factory.

Create a project by profile:

```bash
python3 factory/project-factory.py \
  --profile ai-saas \
  --name "AI Lead Qualifier" \
  --slug ai-lead-qualifier \
  --packs auth,multitenancy,rag,analytics \
  --output ../ai-lead-qualifier
```

Available profiles:

`landing`, `content-site`, `saas`, `ai-saas`, `dashboard`, `marketplace`, `telegram`, `api`, `internal-tool`, `agentic-system`

Available packs:

`auth`, `multitenancy`, `payments`, `ai`, `rag`, `telegram`, `seo`, `analytics`, `content`, `files`

The factory produces a right-sized APES-26 project and records its exact composition in `docs/FACTORY-MANIFEST.json`.
