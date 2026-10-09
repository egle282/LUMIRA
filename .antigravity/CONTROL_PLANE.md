# AI PROJECT OS v8 — Control Plane

v8 adds four persistent intelligence layers:

1. **Knowledge Retrieval** — find relevant validated lessons/skills before work.
2. **Agent Memory** — capture measurable engineering outcomes to improve routing.
3. **Auto-Regression** — turn recurring lessons into proposed regression specs.
4. **Architecture Drift** — detect divergence between declared and implemented architecture.

Commands:

```bash
.antigravity/run "your task"

python .antigravity/control-plane/runtime/control_plane.py retrieve "RAG tenant isolation"

python .antigravity/control-plane/runtime/control_plane.py regress

python .antigravity/control-plane/runtime/control_plane.py drift

python .antigravity/control-plane/runtime/control_plane.py evolve
```

## Operating principle

The Control Plane observes, retrieves, proposes and evaluates.
It does not silently rewrite source code or governing rules.

Knowledge is promoted only after evidence + evaluation + appropriate approval.
