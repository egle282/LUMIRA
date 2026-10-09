# How Antigravity should invoke the Director

Before a meaningful implementation task:

```bash
python .antigravity/router/runtime/director.py --json "<USER TASK>"
```

Read the resulting manifest.

Then:
1. load always_load files;
2. load selected agent files;
3. load selected skill files;
4. inspect the owning project module;
5. execute the relevant workflow;
6. validate;
7. review the diff.

The route manifest is advisory but deterministic. Repository evidence and project-specific rules override generic classification.
