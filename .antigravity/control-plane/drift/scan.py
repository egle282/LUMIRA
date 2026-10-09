#!/usr/bin/env python3
"""Lightweight architecture drift scanner."""
import argparse,json,re
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",default=".")
    ap.add_argument("--architecture",default=".antigravity")
    a=ap.parse_args(); root=Path(a.root); ant=Path(a.architecture)
    rules=[]
    for f in [ant/"rules"/"architecture.md",ant/"rules"/"coding.md",ant/"AI_PROJECT_OS.md"]:
        if f.exists(): rules.append(f.read_text(encoding="utf-8",errors="ignore"))
    findings=[]
    # Detect common accidental artifacts; project-specific architecture checks can be added later.
    for p in root.rglob("*"):
        if not p.is_file() or any(x in p.parts for x in {".git","node_modules",".venv","dist","build"}): continue
        rel=str(p.relative_to(root)).replace("\\","/")
        if rel.endswith((".py",".ts",".tsx",".js",".jsx")):
            txt=p.read_text(encoding="utf-8",errors="ignore")
            if "TODO: ARCHITECTURE" in txt:
                findings.append({"path":rel,"type":"architecture-marker","detail":"Unresolved architecture marker"})
    result={"schema_version":"1.0","findings":findings,"rules_loaded":len(rules),
            "status":"clean" if not findings else "drift-detected"}
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
