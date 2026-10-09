# APES-26 Project Factory

The Project Factory turns the APES-26 master template into a right-sized project scaffold.

## Core command

From the APES-26 repository:

```bash
python3 factory/project-factory.py \
  --profile ai-saas \
  --name "AI Lead Qualifier" \
  --slug ai-lead-qualifier \
  --output ../ai-lead-qualifier
```

Add capability packs when needed:

```bash
python3 factory/project-factory.py \
  --profile ai-saas \
  --name "AI Lead Qualifier" \
  --slug ai-lead-qualifier \
  --packs auth,multitenancy,rag,payments,analytics \
  --output ../ai-lead-qualifier
```

## What the factory does

1. Copies the APES-26 core operating contract.
2. Selects the project profile.
3. Selects only the required docs, skills and agents.
4. Adds capability packs.
5. Creates project metadata.
6. Creates an initial acceptance-criteria file.
7. Creates a generated-project manifest.
8. Adds a project-specific `AGENTS.md` header.
9. Runs the generated-project doctor.

## Profiles

- landing
- content-site
- saas
- ai-saas
- dashboard
- marketplace
- telegram
- api
- internal-tool
- agentic-system

## Capability packs

- auth
- multitenancy
- payments
- ai
- rag
- telegram
- seo
- analytics
- content
- files

## Design principle

The master template contains the complete engineering system.

A generated project is deliberately smaller: it receives only the capabilities relevant to its declared profile and packs.

This prevents every project from carrying irrelevant agents and rules while preserving a single source of truth in APES-26.
