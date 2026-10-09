#!/usr/bin/env python3
"""Generate regression-test specifications from structured lessons. Specs only."""
import argparse,json,re
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--lessons",default=".antigravity/evolution/proposals")
    ap.add_argument("--out",default=".antigravity/control-plane/regression/generated")
    a=ap.parse_args(); src=Path(a.lessons); out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
    made=0
    for p in src.glob("*.md"):
        text=p.read_text(encoding="utf-8",errors="ignore")
        slug=re.sub(r"[^a-z0-9_-]+","-",p.stem.lower()).strip("-")
        f=out/(slug+".json")
        if f.exists(): continue
        spec={"schema_version":"1.0","source":str(p),
              "status":"proposed",
              "checks":[
                "Reproduce the condition described by the lesson.",
                "Verify the corrective pattern.",
                "Verify the original failure no longer occurs.",
                "Verify no adjacent regression was introduced."
              ]}
        f.write_text(json.dumps(spec,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); made+=1
    print(json.dumps({"generated":made,"output":str(out)},ensure_ascii=False))
if __name__=="__main__": main()
