#!/usr/bin/env python3
import argparse,json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--agent",required=True); ap.add_argument("--outcome",choices=["success","partial","failure"],required=True)
    ap.add_argument("--review-findings",type=int,default=0); ap.add_argument("--test-failures",type=int,default=0)
    a=ap.parse_args(); p=Path(".antigravity/control-plane/agent-memory/scorecard.json")
    d=json.loads(p.read_text(encoding="utf-8")); x=d["agents"].setdefault(a.agent,{
      "tasks_completed":0,"successful_first_pass":0,"rework_count":0,"reviewer_findings":0,"test_failures":0})
    x["tasks_completed"]+=1; x["reviewer_findings"]+=a.review_findings; x["test_failures"]+=a.test_failures
    if a.outcome=="success": x["successful_first_pass"]+=1
    if a.outcome in ("partial","failure"): x["rework_count"]+=1
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(x,ensure_ascii=False))
if __name__=="__main__": main()
