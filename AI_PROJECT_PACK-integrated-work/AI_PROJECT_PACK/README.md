# Universal AI Project Pack

This folder is the single-copy distribution package for AI-assisted software projects. It contains one canonical instruction source and platform adapters. The installer copies only the selected adapters into a target project; it does not copy credentials, local memory, backups or platform sessions.

## Quick start

```bash
cd AI_PROJECT_PACK
./install.sh --target /path/to/new-project --all
```

Preview without changes:

```bash
./install.sh --target /path/to/new-project --all --dry-run
```

The installer creates a manifest at `.ai-pack/installation.json`, preserves existing files as `.ai-pack/backup/<timestamp>/`, and never overwrites an existing non-pack file without `--force`.

## Architecture

`source/` is the canonical reusable pack. `adapters/` contains platform-specific projections. `scripts/` contains installation and validation. `platform-manifest.json` records the confidence level of every adapter.

Official platform formats are used where documentation confirms them. For platforms without a stable public project-file convention, the adapter creates a small README fallback pointing back to root `AGENTS.md`; it does not invent unsupported settings or write API keys.

## Updating the pack

Edit canonical files in `source/`, update adapters only when the platform format changes, run `./scripts/smoke-test.sh`, then bump the version in `platform-manifest.json`. Do not edit generated target files manually as a substitute for changing the canonical source.


## Included System Design knowledge

The pack now includes a reusable `system-design-architect` skill with a modular knowledge base covering:
- distributed systems and consistency;
- databases, partitioning and sharding;
- cache, load balancing and CDN;
- Kafka and messaging;
- microservices and APIs;
- reliability, observability and security;
- architecture patterns and canonical design problems;
- AI/LLM/RAG system design;
- HLD, architecture-review and ADR templates;
- worked examples, including an AI Lead Qualifier architecture.

Claude Code receives the skill under `.claude/skills/system-design-architect/`.
Antigravity receives it under `.agents/skills/system-design-architect/` through the Antigravity adapter.
