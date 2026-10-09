#!/usr/bin/env python3
"""Run the controlled evolution pipeline."""
import argparse, subprocess, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
def run(script,args):
    p=subprocess.run([sys.executable,str(HERE/script),*args],text=True,capture_output=True)
    print(p.stdout.strip())
    if p.returncode: print(p.stderr.strip(),file=sys.stderr)
    return p.returncode

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--min-count",type=int,default=3)
    a=ap.parse_args()
    rc=run("pattern_miner.py",["--min-count",str(a.min_count)])
    if rc: return rc
    rc=run("lesson_proposer.py",["--min-count",str(a.min_count)])
    if rc: return rc
    rc=run("knowledge_graph.py",[])
    return rc
if __name__=="__main__": raise SystemExit(main())
