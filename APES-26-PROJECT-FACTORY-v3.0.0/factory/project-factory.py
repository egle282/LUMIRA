#!/usr/bin/env python3
"""
APES-26 Project Factory
Standard-library-only generator.

Example:
python3 factory/project-factory.py \
  --profile ai-saas \
  --name "AI Lead Qualifier" \
  --slug ai-lead-qualifier \
  --packs auth,multitenancy,rag \
  --output ../ai-lead-qualifier
"""
from __future__ import annotations
import argparse
import json
import shutil
import sys
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "factory" / "catalog.json"

def load_catalog():
    return json.loads(CATALOG.read_text(encoding="utf-8"))

def die(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(2)

def copy_selected(src_root: Path, dst_root: Path, relative_paths: list[str]):
    for rel in relative_paths:
        src = src_root / rel
        if not src.exists():
            die(f"Missing factory source: {src}")
        dst = dst_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

def safe_slug(value):
    value = value.strip().lower()
    value = value.replace("_", "-").replace(" ", "-")
    value = "".join(c for c in value if c.isalnum() or c == "-")
    while "--" in value:
        value = value.replace("--", "-")
    return value.strip("-")

def main():
    ap = argparse.ArgumentParser(description="Create an APES-26 project.")
    ap.add_argument("--profile", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--packs", default="")
    ap.add_argument("--description", default="")
    ap.add_argument("--stage", default="mvp")
    ap.add_argument("--architecture", default="modular-monolith")
    args = ap.parse_args()

    catalog = load_catalog()
    if args.profile not in catalog["profiles"]:
        die(f"Unknown profile '{args.profile}'. Available: {', '.join(catalog['profiles'])}")

    slug = safe_slug(args.slug)
    if not slug:
        die("Invalid slug.")

    pack_names = [x.strip() for x in args.packs.split(",") if x.strip()]
    for p in pack_names:
        if p not in catalog["packs"]:
            die(f"Unknown pack '{p}'. Available: {', '.join(catalog['packs'])}")

    out = Path(args.output).expanduser().resolve()
    if out.exists() and any(out.iterdir()):
        die(f"Output directory is not empty: {out}")
    out.mkdir(parents=True, exist_ok=True)

    profile = catalog["profiles"][args.profile]

    # Core docs
    core_docs = [
        "PRODUCT", "UX", "ARCHITECTURE", "AI", "EVALUATION",
        "SECURITY", "TESTING", "DEPLOYMENT", "QUALITY-GATE", "LIFECYCLE", "OBSERVABILITY"
    ]
    selected_docs = set(profile["docs"])
    selected_docs.update(["LIFECYCLE", "QUALITY-GATE"])

    # Always keep core operating contract, project metadata and docs map.
    copy_selected(ROOT, out, [
        "AGENTS.md",
        "README.md",
        "TEMPLATE-VERSION",
        ".gitignore",
        ".env.example",
    ])

    for doc in sorted(selected_docs):
        src = ROOT / "docs" / f"{doc}.md"
        if src.exists():
            copy_selected(ROOT, out, [f"docs/{doc}.md"])

    # ADR template
    copy_selected(ROOT, out, ["docs/adr/000-template.md"])

    # Skills
    selected_skills = set(profile["skills"])
    for p in pack_names:
        selected_skills.update(catalog["packs"][p]["skills"])
    for skill in sorted(selected_skills):
        src = ROOT / ".agents" / "skills" / skill
        if src.exists():
            target = out / ".agents" / "skills" / skill
            shutil.copytree(src, target)

    # Agents
    selected_agents = set(profile["agents"])
    for p in pack_names:
        selected_agents.update(catalog["packs"][p]["agents"])
    for agent in sorted(selected_agents):
        src_dir = ROOT / ".agents" / "agents" / agent
        src_file = ROOT / ".agents" / "agents" / f"{agent}.md"
        target = out / ".agents" / "agents" / agent
        target.mkdir(parents=True, exist_ok=True)
        if src_dir.exists():
            shutil.copytree(src_dir, target, dirs_exist_ok=True)
        elif src_file.exists():
            shutil.copy2(src_file, target / "agent.md")

    # Rules
    core_rules = ["00-core.md", "10-frontend.md", "20-backend.md", "30-ai.md", "40-security.md"]
    for rule in core_rules:
        src = ROOT / ".agents" / "rules" / rule
        if src.exists():
            copy_selected(ROOT, out, [f".agents/rules/{rule}"])
    for p in pack_names:
        rule_name = p if p in {"auth","multitenancy","payments","telegram","seo","analytics","content","files"} else ("ai-production" if p == "ai" else p)
        src = ROOT / "factory" / "templates" / "rules" / f"{rule_name}.md"
        if src.exists():
            target = out / ".agents" / "rules" / src.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)

    # Capability docs
    for p in pack_names:
        for doc in catalog["packs"][p]["docs"]:
            src = ROOT / "factory" / "templates" / doc
            if src.exists():
                target = out / "docs" / doc
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, target)

    # Pack skills from factory templates
    for p in pack_names:
        for skill in catalog["packs"][p]["skills"]:
            src = ROOT / "factory" / "templates" / "skills" / skill
            if src.exists():
                target = out / ".agents" / "skills" / skill
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(src, target, dirs_exist_ok=True)

    # Project metadata
    project_yaml = f"""project:
  name: "{args.name.replace('"', '\\"')}"
  slug: "{slug}"
  type: "{args.profile}"
  stage: "{args.stage}"
  description: "{args.description.replace('"', '\\"')}"
  generated_by: "APES-26 Project Factory v{catalog['version']}"
  generated_at: "{date.today().isoformat()}"

engineering:
  architecture_style: "{args.architecture}"
  stack_status: "to-be-decided"
  verification: "evidence-based"

capabilities:
  profile: "{args.profile}"
  packs: [{", ".join(repr(x) for x in pack_names)}]

quality:
  accessibility_target: "WCAG 2.2 AA"
  browser_verification: true
  security_review: true
  ai_evaluation: {"true" if ("ai" in pack_names or args.profile in {"ai-saas","telegram","agentic-system"}) else "false"}
  release_quality_gate: true
"""
    (out / "PROJECT.yaml").write_text(project_yaml, encoding="utf-8")

    # Acceptance criteria starter
    (out / "docs/ACCEPTANCE.md").write_text(f"""# Acceptance Criteria — {args.name}

## Product outcome

Define the measurable outcome before implementation.

## Primary user journey

1.
2.
3.

## Acceptance criteria

- [ ] AC-001:
- [ ] AC-002:
- [ ] AC-003:

## Non-goals

- 

## Verification evidence

Document actual checks here after implementation.
""", encoding="utf-8")

    # Factory manifest
    manifest = {
        "factory_version": catalog["version"],
        "generated_at": date.today().isoformat(),
        "profile": args.profile,
        "packs": pack_names,
        "selected_docs": sorted(selected_docs),
        "selected_skills": sorted(selected_skills),
        "selected_agents": sorted(selected_agents),
        "architecture": args.architecture,
    }
    (out / "docs/FACTORY-MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    # Project-specific README
    readme = out / "README.md"
    original = readme.read_text(encoding="utf-8")
    header = f"""# {args.name}

Generated by **APES-26 Project Factory v{catalog['version']}**.

Profile: `{args.profile}`

Capabilities: {", ".join(pack_names) if pack_names else "none"}

## First commands

1. Review `PROJECT.yaml`.
2. Complete `docs/PRODUCT.md`.
3. Complete `docs/ACCEPTANCE.md`.
4. Run `/plan` for the first non-trivial implementation.
5. Verify before claiming completion.

---

"""
    readme.write_text(header + original, encoding="utf-8")

    print(f"Created APES-26 project: {out}")
    print(f"Profile: {args.profile}")
    print(f"Packs: {', '.join(pack_names) if pack_names else 'none'}")
    print("Next: review PRODUCT.md and ACCEPTANCE.md, then use /plan.")

if __name__ == "__main__":
    main()
