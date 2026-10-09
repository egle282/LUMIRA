#!/usr/bin/env python3
"""AI PROJECT OS v8 Control Plane."""
import argparse, subprocess, sys, json
from pathlib import Path

ROOT=Path(".antigravity/control-plane")
def run(script,args):
    p=subprocess.run([sys.executable,str(ROOT/script),*args],text=True,capture_output=True)
    if p.stdout.strip(): print(p.stdout.strip())
    if p.returncode: raise SystemExit(p.stderr or p.stdout)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("command",choices=["retrieve","regress","drift","evolve"])
    ap.add_argument("query",nargs="*")
    a=ap.parse_args()
    if a.command=="retrieve":
        run("retrieval/retrieve.py",[" ".join(a.query)])
    elif a.command=="regress":
        run("regression/generate.py",[])
    elif a.command=="drift":
        run("drift/scan.py",[])
    elif a.command=="evolve":
        evo=Path(".antigravity/evolution/engine/evolve.py")
        p=subprocess.run([sys.executable,str(evo)],text=True,capture_output=True)
        print(p.stdout)
        if p.returncode: raise SystemExit(p.stderr)
if __name__=="__main__": main()
