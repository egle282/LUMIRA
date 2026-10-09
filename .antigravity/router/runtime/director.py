#!/usr/bin/env python3
"""AI PROJECT OS Director Runtime.

Deterministic first-pass task router for Antigravity/Gemini.
It inspects lightweight repository signals and emits an inspectable route manifest.
It never edits source files.
"""

from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

ROOT = Path.cwd()
AG = ROOT / ".antigravity"

AGENTS = {
    "product": "agents/product.md",
    "architect": "agents/architect.md",
    "backend": "agents/backend.md",
    "frontend": "agents/frontend.md",
    "ai-engineer": "agents/ai-engineer.md",
    "database": "agents/database.md",
    "qa": "agents/qa.md",
    "security": "agents/security.md",
    "seo": "agents/seo.md",
    "devops": "agents/devops.md",
    "reviewer": "agents/reviewer.md",
    "director": "agents/director.md",
}

SKILLS = {
    "architecture": "skills/ai-project-os/architecture/SKILL.md",
    "api-design": "skills/ai-project-os/api-design/SKILL.md",
    "database-design": "skills/ai-project-os/database-design/SKILL.md",
    "ai-engineering": "skills/ai-project-os/ai-engineering/SKILL.md",
    "rag": "skills/ai-project-os/rag/SKILL.md",
    "prompt-engineering": "skills/ai-project-os/prompt-engineering/SKILL.md",
    "testing": "skills/ai-project-os/testing/SKILL.md",
    "security": "skills/ai-project-os/security/SKILL.md",
    "seo": "skills/ai-project-os/seo/SKILL.md",
    "deployment": "skills/ai-project-os/deployment/SKILL.md",
    "observability": "skills/ai-project-os/observability/SKILL.md",
}

PATTERNS = {
    "product": r"\b(product|mvp|icp|пользоват|продукт|монетизац|воронк|user journey)\b",
    "architecture": r"\b(architect|architecture|архитектур|module|модул|refactor|рефактор)\b",
    "ai": r"\b(ai|llm|gemini|openai|anthropic|model|модель|prompt|промпт|agent|агент)\b",
    "rag": r"\b(rag|vector|embedding|embedd|knowledge base|баз[ае] знаний|pdf|документ)\b",
    "backend": r"\b(api|backend|бекенд|endpoint|route|fastapi|hono|server|сервер)\b",
    "frontend": r"\b(frontend|ui|ux|react|next\.?js|vite|css|button|кнопк|экран|страниц)\b",
    "database": r"\b(database|db|postgres|postgresql|supabase|schema|migration|миграц|таблиц|sql)\b",
    "security": r"\b(security|auth|authentication|authorization|permission|permissions|tenant|pii|secret|secrets|payment|payments|webhook|privacy|безопас|авторизац|оплат)\b",
    "seo": r"\b(seo|robots|sitemap|canonical|open.?graph|json.?ld|schema\.org|мета|индексац)\b",
    "devops": r"\b(deploy|deployment|production|prod|docker|terraform|ci|cd|vercel|cloud|релиз|деплой)\b",
    "bug": r"\b(bug|fix|broken|error|ошиб|слом|не работает|исправ)\b",
    "test": r"\b(test|tests|testing|qa|e2e|playwright|тест|провер)\b",
    "docs": r"\b(document|documentation|docs|readme|md|документац)\b",
}

def scan_repo():
    names = set()
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if ".git" in p.parts:
            continue
        names.add(p.name.lower())
    return {
        "python": any(n in names for n in ["pyproject.toml", "requirements.txt", "pipfile"]),
        "typescript": any(n in names for n in ["package.json", "tsconfig.json"]),
        "docker": "dockerfile" in names or "docker-compose.yml" in names,
        "supabase": "supabase" in names,
        "terraform": any("terraform" in n for n in names),
    }

def classify(text: str):
    t = text.lower()
    hits = {k: bool(re.search(v, t, re.I)) for k, v in PATTERNS.items()}

    if hits["product"] and not any(hits[k] for k in ["backend","frontend","database","ai","security","seo","devops","bug"]):
        task_type = "product"
    elif hits["bug"]:
        task_type = "bug"
    elif hits["ai"] or hits["rag"]:
        task_type = "ai"
    elif hits["database"]:
        task_type = "database"
    elif hits["frontend"]:
        task_type = "frontend"
    elif hits["backend"]:
        task_type = "backend"
    elif hits["seo"]:
        task_type = "seo"
    elif hits["devops"]:
        task_type = "deployment"
    elif hits["docs"]:
        task_type = "documentation"
    else:
        task_type = "feature"

    high = bool(re.search(PATTERNS["security"], t))
    medium = any(hits[k] for k in ["backend","frontend","database","ai","bug","test"])
    risk = "high" if high else "medium" if medium else "low"

    if any(x in t for x in ["production", "prod", "delete", "drop ", "reset", "destroy", "секрет", "продакшн", "удалить"]):
        risk = "high"

    scope = "cross-module" if sum(hits[k] for k in ["backend","frontend","database","ai","security","devops"]) >= 2 else "module"

    return task_type, risk, scope, hits

def route(task_type, risk, scope, hits):
    agents = ["director"]
    skills = []

    if task_type == "product":
        agents += ["product"]
    elif task_type == "bug":
        if hits["frontend"]: agents += ["frontend"]
        elif hits["database"]: agents += ["database"]
        elif hits["ai"] or hits["rag"]: agents += ["ai-engineer"]
        else: agents += ["backend"]
        skills += ["testing"]
    elif task_type == "ai":
        agents += ["ai-engineer"]
        skills += ["ai-engineering", "testing", "observability"]
        if hits["rag"]:
            skills += ["rag"]
            agents += ["database"]
    elif task_type == "database":
        agents += ["database", "backend", "qa"]
        skills += ["database-design", "testing"]
    elif task_type == "frontend":
        agents += ["frontend", "qa"]
        skills += ["testing"]
    elif task_type == "backend":
        agents += ["backend", "qa"]
        skills += ["api-design", "testing"]
    elif task_type == "seo":
        agents += ["frontend", "seo", "qa"]
        skills += ["seo", "testing"]
    elif task_type == "deployment":
        agents += ["devops", "qa"]
        skills += ["deployment", "testing"]
    elif task_type == "documentation":
        agents += ["reviewer"]
    else:
        agents += ["architect"]

    if scope == "cross-module":
        if "architect" not in agents: agents.insert(1, "architect")
        if "architecture" not in skills: skills.append("architecture")

    if risk == "high":
        if "security" not in agents: agents.append("security")
        if "security" not in skills: skills.append("security")

    if "reviewer" not in agents:
        agents.append("reviewer")

    # Stable de-duplication.
    agents = list(dict.fromkeys(agents))
    skills = list(dict.fromkeys(skills))
    return agents, skills

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("task", nargs="+")
    args = parser.parse_args()
    task = " ".join(args.task)

    task_type, risk, scope, hits = classify(task)
    agents, skills = route(task_type, risk, scope, hits)
    repo = scan_repo()

    manifest = {
        "version": "1.0",
        "task": task,
        "classification": {
            "type": task_type,
            "risk": risk,
            "scope": scope,
        },
        "agents": agents,
        "skills": skills,
        "always_load": [
            ".antigravity/SYSTEM.md",
            ".antigravity/AGENTS.md",
            ".antigravity/CAPABILITY_LEDGER.md",
        ],
        "repo_signals": repo,
        "human_authorization": risk == "high",
        "validation": [
            "focused tests",
            "build/typecheck where applicable",
            "final diff review",
        ],
    }

    if args.json:
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return

    print("AI PROJECT OS — DIRECTOR ROUTE")
    print("=" * 34)
    print(f"Task: {task}")
    print(f"Type: {task_type}")
    print(f"Risk: {risk}")
    print(f"Scope: {scope}")
    print("\nAgents:")
    for a in agents:
        print(f"  - {a}: {AGENTS.get(a, 'project-specific')}")
    print("\nSkills:")
    for s in skills:
        print(f"  - {s}: {SKILLS.get(s, 'project-specific')}")
    print("\nAlways load:")
    for x in manifest["always_load"]:
        print(f"  - {x}")
    print(f"\nHuman authorization required: {'YES' if risk == 'high' else 'NO'}")
    print("\nNext: inspect the selected files, create a short plan, then implement and validate.")

if __name__ == "__main__":
    main()
