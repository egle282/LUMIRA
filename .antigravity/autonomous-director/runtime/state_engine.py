#!/usr/bin/env python3
"""Build a lightweight project state snapshot from available evidence."""
import argparse,json,datetime
from pathlib import Path

def count_files(root, exts):
    n=0
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts and not any(x in p.parts for x in {".git","node_modules",".venv","dist","build"}): n+=1
    return n
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--root",default="."); ap.add_argument("--out",default=".antigravity/autonomous-director/state/project_state.json")
    a=ap.parse_args(); root=Path(a.root)
    exists=lambda *parts:(root.joinpath(*parts)).exists()
    health={
      "architecture":1 if exists(".antigravity","AI_PROJECT_OS.md") else 0,
      "database":1 if any(exists(x) for x in ["supabase","migrations","alembic"]) else 0,
      "api":1 if any(exists(x) for x in ["openapi.yaml","openapi.yml"]) or count_files(root,{".py",".ts",".js"}) else 0,
      "frontend":1 if any(exists(x) for x in ["src","app","pages"]) else 0,
      "ai":1 if exists(".antigravity","skills","ai-engineering") else 0,
      "tests":1 if exists("tests","test") else 0,
      "security":1 if exists(".antigravity","rules","security.md") else 0,
      "documentation":1 if exists("README.md") else 0
    }
    state={"schema_version":"1.0","project":{"root":str(root.resolve())},"health":health,
           "risks":[],"debt":[],"open_proposals":[],"updated_at":datetime.datetime.now().isoformat()}
    p=root/a.out if not str(a.out).startswith("/") else Path(a.out)
    p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(state,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
