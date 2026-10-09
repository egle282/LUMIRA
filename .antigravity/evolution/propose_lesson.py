#!/usr/bin/env python3
"""Create a structured lesson proposal from an incident/outcome note."""
import argparse
from pathlib import Path
from datetime import datetime

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--trigger",required=True)
    ap.add_argument("--observation",required=True)
    ap.add_argument("--root-cause",default="TBD")
    ap.add_argument("--evidence",default="TBD")
    ap.add_argument("--target",default="skill")
    a=ap.parse_args()
    stamp=datetime.now().strftime("%Y%m%d-%H%M%S")
    p=Path(".antigravity/evolution/proposals")
    p.mkdir(parents=True,exist_ok=True)
    f=p/f"LESSON-{stamp}.md"
    f.write_text(f"""# Lesson Proposal {stamp}

- Trigger: {a.trigger}
- Observation: {a.observation}
- Root cause: {a.root_cause}
- Evidence: {a.evidence}
- Confidence: low
- Promotion target: {a.target}
- Status: proposed

## Validation required
- Reproduce or verify the observation.
- Check for counterexamples.
- Confirm no security/safety regression.
- Add a regression test where practical.
""",encoding="utf-8")
    print(f)

if __name__=="__main__": main()
