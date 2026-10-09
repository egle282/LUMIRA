# Context Loader v1
Converts a routed task into a bounded, relevant set of project files.

Pipeline:
`Task → Director → Router → Context Loader → context_manifest.json → Agents/Skills → Gemini → QA → Reviewer`

Run:
```bash
python .antigravity/router/runtime/context_loader.py --json "Добавь RAG по PDF с tenant isolation"
```

Write a manifest:
```bash
python .antigravity/router/runtime/context_loader.py --write .antigravity/router/runtime/context_manifest.json "your task"
```

Rules: never include secrets; never treat generated files as authoritative; always include project-level agent/rule files when present; keep context bounded; do not modify source files.
