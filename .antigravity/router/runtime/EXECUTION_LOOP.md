# Execution Loop v2
1. Director — classify risk/scope/agents/skills.
2. Router — resolve route.
3. Context Loader — discover bounded relevant context.
4. Manifest — freeze selected paths for this execution.
5. Agents — execute within scope/contracts.
6. QA — tests/checks.
7. Reviewer — inspect diff, contracts, security, regressions.
8. Release gate — deploy only when required checks pass.

Example:
```bash
python .antigravity/router/runtime/director.py --json "Добавь RAG по PDF с tenant isolation"
python .antigravity/router/runtime/context_loader.py --write .antigravity/router/runtime/context_manifest.json "Добавь RAG по PDF с tenant isolation"
```
