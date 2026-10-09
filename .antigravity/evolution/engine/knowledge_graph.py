#!/usr/bin/env python3
"""Build a small file-backed knowledge graph from validated lessons/rules/skills."""
import argparse, json, re
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",default=".antigravity")
    ap.add_argument("--out",default=".antigravity/evolution/knowledge/graph.json")
    a=ap.parse_args()
    root=Path(a.root); nodes=[]; rel=[]
    sources=[
      ("lesson",root/"evolution"/"LESSONS.md"),
      ("skill",root/"skills"),
      ("rule",root/"rules"),
      ("workflow",root/"workflows")
    ]
    for typ,p in sources:
        files=[p] if p.is_file() else list(p.rglob("*")) if p.exists() else []
        for f in files:
            if not f.is_file(): continue
            nid=f"{typ}:{f.relative_to(root).as_posix()}"
            title=f.stem.replace("_"," ").replace("-"," ")
            nodes.append({"id":nid,"type":typ,"title":title,"status":"active",
                          "confidence":1.0,"evidence":[str(f)]})
    out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({"schema_version":"1.0","nodes":nodes,"relations":rel,
                               "policy":"Validated knowledge only; proposals remain outside active graph."},
                              ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"nodes":len(nodes),"relations":len(rel),"output":str(out)},ensure_ascii=False))
if __name__=="__main__": main()
