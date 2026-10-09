# Self-Evolution Policy

The system improves through a controlled feedback loop:

```text
Execution
  ↓
Evidence
  ↓
Outcome Log
  ↓
Failure / Success Pattern
  ↓
Lesson Proposal
  ↓
Validation
  ↓
Human/Reviewer Gate
  ↓
Rule / Skill / Workflow update
  ↓
Regression Evaluation
  ↓
New baseline
```

## What may evolve automatically
- candidate prompts
- routing heuristics
- retrieval keywords
- test cases
- documentation suggestions
- draft lessons

## What requires approval
- security rules
- authorization/RLS behavior
- payment logic
- production deployment policy
- destructive database operations
- system-wide agent instructions
- changes that weaken safety gates

## Principle
The system may *propose* self-improvement automatically, but it must not silently rewrite its own governing rules.
