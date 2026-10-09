# AI PROJECT OS v9 — Autonomous Project Director

## One command

```bash
.antigravity/run "your task"
```

The Director automatically:
1. routes the task
2. classifies risk
3. builds project state
4. loads bounded context
5. retrieves relevant validated knowledge
6. creates an execution bundle
7. enforces approval gates
8. hands the plan to agents
9. expects QA/review
10. records evidence for evolution

## High-risk task

```bash
.antigravity/run --approve "Add production RLS migration"
```

`--approve` is an explicit approval signal for the current execution. Critical
operations still require project-specific/manual safeguards.

## Design goal

The user should think in outcomes, not in agent names, files or command sequences.
