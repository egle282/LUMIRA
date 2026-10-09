#!/usr/bin/env python3
"""Validate whether a lesson proposal is eligible for promotion."""
import argparse, re
from pathlib import Path

SENSITIVE=["security","auth","authorization","rls","tenant","payment","production","deploy",
           "secret","credential","database","migration","destructive"]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("proposal")
    ap.add_argument("--approved",action="store_true")
    a=ap.parse_args()
    text=Path(a.proposal).read_text(encoding="utf-8").lower()
    sensitive=any(x in text for x in SENSITIVE)
    checks={
      "has_evidence":"evidence" in text,
      "has_validation":"validation" in text,
      "has_status":"status" in text,
      "sensitive_change_requires_approval": (not sensitive) or a.approved
    }
    ok=all(checks.values())
    print({"eligible":ok,"checks":checks,"sensitive":sensitive})
    return 0 if ok else 2
if __name__=="__main__": raise SystemExit(main())
