#!/usr/bin/env python3
"""Convert repeated patterns into proposed lessons. Draft-only, never auto-promotes."""
import argparse, json
from pathlib import Path
from datetime import datetime

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--patterns",default=".antigravity/evolution/patterns/patterns.json")
    ap.add_argument("--min-count",type=int,default=3)
    a=ap.parse_args()
    d=json.loads(Path(a.patterns).read_text(encoding="utf-8"))
    out=Path(".antigravity/evolution/proposals"); out.mkdir(parents=True,exist_ok=True)
    made=0
    for x in d.get("patterns",[]):
        if x["count"]<a.min_count: continue
        slug=x["pattern"].replace("/","-").replace(" ","-")[:50]
        f=out/f"LESSON-PROPOSED-{slug}.md"
        if f.exists(): continue
        f.write_text(f"""# Proposed Lesson: {x["pattern"]}

- Status: proposed
- Evidence count: {x["count"]}
- Evidence IDs: {", ".join(x["evidence_ids"])}

## Hypothesis
The repeated occurrence of `{x["pattern"]}` indicates a potentially reusable engineering pattern.

## Required validation
1. Inspect the evidence.
2. Determine whether the occurrences share a root cause or successful solution.
3. Add a regression test or concrete verification where practical.
4. Check for security and architecture regressions.
5. Promote only after reviewer/human approval.
""",encoding="utf-8")
        made+=1
    print(json.dumps({"proposals_created":made},ensure_ascii=False))
if __name__=="__main__": main()
