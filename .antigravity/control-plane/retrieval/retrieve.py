#!/usr/bin/env python3
"""Retrieve relevant validated knowledge from local AI PROJECT OS files."""
import argparse, json, re
from pathlib import Path

STOP={"the","and","with","this","that","для","что","как","это","при","если","через","добавь","сделай"}

def tok(s): return {x for x in re.findall(r"[a-zA-Zа-яА-ЯёЁ0-9_-]{4,}",s.lower()) if x not in STOP}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("query"); ap.add_argument("--root",default=".antigravity")
    ap.add_argument("--top-k",type=int,default=8)
    a=ap.parse_args(); q=tok(a.query); root=Path(a.root); rows=[]
    for p in root.rglob("*.md"):
        if any(x in p.parts for x in {".git","node_modules",".venv"}): continue
        txt=p.read_text(encoding="utf-8",errors="ignore")
        low=tok(txt)
        overlap=q & low
        if overlap:
            score=len(overlap)/max(1,len(q))
            # Favor validated/active knowledge and evolution material.
            bonus=(0.15 if re.search(r"status:\s*(validated|active)",txt,re.I) else 0)
            rows.append((score+bonus,str(p),sorted(overlap)))
    rows.sort(key=lambda x:(-x[0],x[1]))
    result={"schema_version":"1.0","query":a.query,
            "results":[{"path":p,"score":round(s,4),"matched_tokens":m} for s,p,m in rows[:a.top_k]]}
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
