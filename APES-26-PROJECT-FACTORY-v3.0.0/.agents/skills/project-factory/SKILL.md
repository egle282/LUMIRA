---
name: project-factory
description: Creates right-sized APES-26 projects from a product profile and capability packs, preserving the master engineering contract while avoiding irrelevant skills and agents.
---

# Project Factory Skill

Use when starting a new repository from APES-26.

## Required inputs

- project name
- slug
- profile
- optional capability packs
- optional stack choices
- optional deployment target

## Process

1. Load `factory/catalog.json`.
2. Validate profile and pack names.
3. Compute the union of required docs, skills, agents and rules.
4. Generate the project scaffold.
5. Fill `PROJECT.yaml`.
6. Generate `docs/FACTORY-MANIFEST.md`.
7. Generate initial `docs/ACCEPTANCE.md`.
8. Run the generated-project doctor.
9. Do not start implementation automatically unless explicitly requested.

The factory creates a project scaffold; it does not invent product requirements.
