
## Executable routing

Before meaningful work, run:

```bash
python .antigravity/router/runtime/director.py --json "<USER TASK>"
```

Use the returned manifest to determine the minimum agents and skills to load.
Do not load the entire skills library by default.

## Mandatory Context Loading
Before any non-trivial task:
1. Run Director/Router.
2. Run Context Loader.
3. Read selected files from the manifest.
4. Treat project-specific rules/contracts as authoritative.
5. Never read or expose secret files.
6. Expand context deliberately if the manifest is insufficient.

## AI PROJECT OS v6 — Single Command
For substantial work, prefer:
```bash
.antigravity/run "task"
```
This creates a run bundle containing route, bounded context manifest, and execution plan.

## Self-Evolution
After completed work, record evidence and lessons. Never silently rewrite governing rules. Improvements must pass validation/regression checks and sensitive changes require explicit approval.

## v7 Evolution Engine
After meaningful tasks, record structured experience. Periodically run:
```bash
python .antigravity/evolution/engine/evolve.py
```
Treat generated lessons as proposals until validated. Never silently modify governing rules.

## v8 Control Plane
Before substantial implementation, retrieve relevant validated knowledge:
```bash
python .antigravity/control-plane/runtime/control_plane.py retrieve "TASK"
```
After implementation, run applicable regression and drift checks. Record evidence for future evolution.

## v9 Autonomous Project Director
Use `.antigravity/run "TASK"` as the default entry point for substantial work.
Respect the risk gate and project state. For high/critical operations, stop at the approval gate unless explicit authorization is present.
