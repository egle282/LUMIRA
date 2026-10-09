#!/usr/bin/env python3
"""Single-entry Autonomous Project Director."""
import argparse,json,subprocess,sys,time
from pathlib import Path

ROOT=Path(".antigravity")
def run(script,args,cwd):
    p=subprocess.run([sys.executable,str(script),*args],cwd=cwd,text=True,capture_output=True)
    if p.returncode: raise SystemExit(p.stderr or p.stdout)
    return p.stdout

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("task"); ap.add_argument("--root",default="."); ap.add_argument("--top-k",type=int,default=30)
    ap.add_argument("--approve",action="store_true")
    a=ap.parse_args(); root=Path(a.root).resolve()
    stamp=time.strftime("%Y%m%d-%H%M%S")
    run_dir=root/".antigravity/autonomous-director/runs"/stamp; run_dir.mkdir(parents=True,exist_ok=True)

    # Existing v6 director
    base_director=root/".antigravity/router/runtime/director.py"
    if base_director.exists():
        route=json.loads(run(base_director,["--json",a.task],root))
    else:
        route={"type":"feature","risk":"medium","scope":"module","agents":["director","reviewer"],"skills":[]}

    gate=json.loads(run(ROOT/"autonomous-director/gates/risk_gate.py",[a.task],root))
    state=json.loads(run(ROOT/"autonomous-director/runtime/state_engine.py",["--root",str(root)],root))
    loader=root/".antigravity/router/runtime/context_loader.py"
    manifest=run(loader,["--json","--top-k",str(a.top_k),a.task],root) if loader.exists() else "{}"
    manifest=json.loads(manifest)

    knowledge=[]
    retrieval=root/".antigravity/control-plane/retrieval/retrieve.py"
    if retrieval.exists():
        knowledge=json.loads(run(retrieval,[a.task],root)).get("results",[])

    approval = gate["execution_policy"] in ("auto","auto_with_review") or a.approve
    plan={
      "schema_version":"1.0","run_id":stamp,"task":a.task,
      "route":route,"risk_gate":gate,"approval_granted":approval,
      "project_state":state,
      "context_manifest":manifest,
      "relevant_knowledge":knowledge,
      "execution":{"status":"authorized_for_agent" if approval else "blocked_pending_approval",
                   "source_modified":False},
      "required_sequence":["plan","implement","test","review","record-experience","update-state"]
    }
    (run_dir/"execution.json").write_text(json.dumps(plan,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(plan,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
