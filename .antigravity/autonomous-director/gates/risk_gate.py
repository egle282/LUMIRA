#!/usr/bin/env python3
"""Deterministic risk classifier / approval gate."""
import argparse,json,re

RULES={
 "critical":["drop database","delete production","rotate production secrets","disable rls",
             "remove authentication","delete all users"],
 "high":["production","payment","stripe","tinkoff","rls","tenant isolation","migration",
         "auth","authorization","secret","credential","deploy"],
 "medium":["database","api","refactor","dependency","schema","redis","queue"],
}
def classify(t):
    x=t.lower()
    for level in ("critical","high","medium"):
        if any(k in x for k in RULES[level]): return level
    return "low"
def policy(level):
    return {"low":"auto","medium":"auto_with_review","high":"approval_required","critical":"human_required"}[level]
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("task"); a=ap.parse_args()
    level=classify(a.task)
    print(json.dumps({"risk":level,"execution_policy":policy(level),
                      "human_approval_required":level in ("high","critical")},ensure_ascii=False,indent=2))
if __name__=="__main__": main()
