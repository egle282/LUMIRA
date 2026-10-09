from pathlib import Path
required = [
    'AGENTS.md','PROJECT.yaml','README.md',
    'docs/PRODUCT.md','docs/UX.md','docs/ARCHITECTURE.md','docs/AI.md',
    'docs/EVALUATION.md','docs/SECURITY.md','docs/TESTING.md',
    'docs/DEPLOYMENT.md','docs/QUALITY-GATE.md','docs/LIFECYCLE.md',
    '.agents/rules/00-core.md',
    '.agents/skills/ai-engineering/SKILL.md',
    '.agents/skills/release-quality-gate/SKILL.md',
]
missing=[p for p in required if not Path(p).exists()]
if missing:
    print('FAIL'); [print(' -',x) for x in missing]; raise SystemExit(1)
print(f'PASS: {len(required)} required files present')
