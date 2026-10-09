# AI PROJECT OS v7 — Evolution Engine

The system now has a controlled learning loop:

```text
TASK
 ↓
DIRECTOR / ROUTER
 ↓
CONTEXT
 ↓
AGENTS
 ↓
QA / REVIEWER
 ↓
EXPERIENCE
 ↓
PATTERN MINER
 ↓
LESSON PROPOSER
 ↓
EVALUATION GATE
 ↓
VALIDATED KNOWLEDGE
 ↓
RULE / SKILL / WORKFLOW
 ↓
REGRESSION EVALUATION
 ↺
```

## Commands

Run engineering task:
```bash
.antigravity/run "your task"
```

Run evolution cycle:
```bash
python .antigravity/evolution/engine/evolve.py
```

Mine patterns only:
```bash
python .antigravity/evolution/engine/pattern_miner.py
```

## Design principle

The AI can discover patterns and propose improvements automatically.
It cannot silently promote changes to governing rules.

Sensitive areas — security, auth, RLS, tenant isolation, payments, production,
destructive DB operations — require explicit approval.

## Knowledge hierarchy

`Core rules > Project facts/contracts > Validated skills/lessons > Proposals > Generic defaults`

The system learns from evidence, not from unverified model output.
