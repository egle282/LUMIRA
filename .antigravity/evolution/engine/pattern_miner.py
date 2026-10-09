#!/usr/bin/env python3
"""Mine repeated engineering patterns from structured experience JSONL."""
import argparse, json, re
from collections import Counter, defaultdict
from pathlib import Path

STOP={"the","and","with","that","this","from","для","что","как","это","при","если","через"}

def tokens(s):
    return [x for x in re.findall(r"[a-zA-Zа-яА-ЯёЁ0-9_-]{4,}",s.lower()) if x not in STOP]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",default=".antigravity/evolution/experience.jsonl")
    ap.add_argument("--out",default=".antigravity/evolution/patterns/patterns.json")
    ap.add_argument("--min-count",type=int,default=3)
    a=ap.parse_args()
    p=Path(a.input)
    if not p.exists():
        print(json.dumps({"patterns":[],"note":"No experience log yet."},ensure_ascii=False)); return
    docs=[json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]
    counters=Counter(); examples=defaultdict(list)
    for d in docs:
        blob=" ".join([d.get("task",""),d.get("outcome","")," ".join(d.get("failures",[])),
                       " ".join(d.get("root_causes",[]))," ".join(d.get("lessons",[]))])
        seen=set(tokens(blob))
        for t in seen:
            counters[t]+=1; examples[t].append(d.get("id","unknown"))
    patterns=[{"pattern":k,"count":v,"evidence_ids":examples[k][:10]}
              for k,v in counters.items() if v>=a.min_count]
    patterns.sort(key=lambda x:(-x["count"],x["pattern"]))
    out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({"schema_version":"1.0","patterns":patterns},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"patterns_found":len(patterns),"output":str(out)},ensure_ascii=False))
if __name__=="__main__": main()
