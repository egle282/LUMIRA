#!/usr/bin/env python3
"""AI PROJECT OS v6 single-command execution orchestrator.

Runs deterministic Director + Context Loader and creates an execution bundle.
It intentionally does not auto-edit source code: implementation remains under
the IDE/agent authorization boundary.
"""
from __future__ import annotations
import argparse, json, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
DIRECTOR = HERE / "director.py"
LOADER = HERE / "context_loader.py"

def run(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if p.returncode:
        raise SystemExit(p.stderr or p.stdout)
    return p.stdout

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("task")
    ap.add_argument("--root", default=".")
    ap.add_argument("--top-k", type=int, default=30)
    ap.add_argument("--execute", action="store_true",
                    help="Mark the bundle ready for agent implementation; does not itself edit source.")
    a = ap.parse_args()
    root = Path(a.root).resolve()
    run_dir = root / ".antigravity" / "router" / "runtime" / "runs"
    run_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    bundle = run_dir / stamp
    bundle.mkdir()

    route = json.loads(run([sys.executable, str(DIRECTOR), "--json", a.task], root))
    (bundle/"route.json").write_text(json.dumps(route, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    manifest_path = bundle/"context_manifest.json"
    run([sys.executable, str(LOADER), "--write", str(manifest_path),
         "--top-k", str(a.top_k), a.task], root)

    plan = {
        "schema_version":"1.0",
        "run_id":stamp,
        "task":a.task,
        "route":route,
        "context_manifest":str(manifest_path.relative_to(root)),
        "phase":"ready-for-agent" if a.execute else "planned",
        "source_modified":False,
        "next_steps":[
            "Read route.json and context_manifest.json.",
            "Retrieve relevant validated lessons/skills before implementation.",
            "Load the selected agent/skill instructions.",
            "Produce an implementation plan before editing for medium/high-risk work.",
            "Run QA and reviewer checks after implementation.",
            "Record outcome in evolution/experience log."
        ]
    }
    (bundle/"execution_plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(plan, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
