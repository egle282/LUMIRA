#!/usr/bin/env python3
from pathlib import Path
import json
import sys

ROOT = Path.cwd()
errors = []

required = [
    "AGENTS.md",
    "PROJECT.yaml",
    "docs/PRODUCT.md",
    "docs/QUALITY-GATE.md",
    ".agents/rules/00-core.md",
]

for rel in required:
    if not (ROOT / rel).exists():
        errors.append(f"missing: {rel}")

if (ROOT / "docs/FACTORY-MANIFEST.json").exists():
    try:
        manifest = json.loads((ROOT / "docs/FACTORY-MANIFEST.json").read_text())
        for rel in manifest.get("selected_skills", []):
            if not (ROOT / ".agents/skills" / rel / "SKILL.md").exists():
                errors.append(f"missing selected skill: {rel}")
        for rel in manifest.get("selected_agents", []):
            if not (ROOT / ".agents/agents" / rel / "agent.md").exists():
                errors.append(f"missing selected agent: {rel}")
    except Exception as exc:
        errors.append(f"invalid FACTORY-MANIFEST.json: {exc}")

if errors:
    print("APES-26 PROJECT DOCTOR: FAIL")
    for e in errors:
        print(" -", e)
    sys.exit(1)

print("APES-26 PROJECT DOCTOR: PASS")
print("Core contract, selected capabilities and manifest are consistent.")
