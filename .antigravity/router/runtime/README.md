# AI PROJECT OS — EXECUTABLE DIRECTOR RUNTIME

This layer turns Director routing rules into a deterministic, inspectable runtime.

It does NOT execute arbitrary code or silently modify the repository.
It produces a route manifest that Antigravity/Gemini can use to load only the required context.

## Command

```bash
python .antigravity/router/runtime/director.py "Добавь RAG по PDF с tenant isolation"
```

Optional JSON output:

```bash
python .antigravity/router/runtime/director.py --json "Исправь оплату"
```

The runtime is intentionally dependency-free Python.
