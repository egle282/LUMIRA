# APES-26 Project Factory

The Project Factory is the layer above the APES-26 master template.

## Architecture

```text
                         APES-26 MASTER
                              |
                    +---------+---------+
                    |                   |
                 PROFILES           CAPABILITY
                    |                 PACKS
                    |                   |
                    +---------+---------+
                              |
                       PROJECT FACTORY
                              |
                              v
                    RIGHT-SIZED PROJECT
                              |
            +-----------------+------------------+
            |                 |                  |
          RULES             SKILLS             AGENTS
            |                 |                  |
            +-----------------+------------------+
                              |
                         PROJECT DOCS
                              |
                            /plan
                              |
                           BUILD
                              |
                        QUALITY GATE
```

## Profile vs capability pack

A **profile** describes the dominant product shape.

A **capability pack** adds a cross-cutting capability.

Example:

```text
profile: ai-saas
packs:
  auth
  multitenancy
  payments
  rag
  analytics
```

This is preferable to creating hundreds of separate product templates.

## Factory invariants

The factory must:

- preserve the APES-26 core contract
- never invent product requirements
- never silently change security defaults
- never include secret values
- keep generated projects independently usable
- record the exact profile/packs in `docs/FACTORY-MANIFEST.json`

## Generated-project lifecycle

The factory stops after scaffolding.

It does not silently start implementation.

The generated project then enters the normal APES-26 lifecycle:

`DISCOVER → SPECIFY → MODEL → UX → DESIGN → ARCHITECT → BUILD → VERIFY → HARDEN → RELEASE → OBSERVE → LEARN`
