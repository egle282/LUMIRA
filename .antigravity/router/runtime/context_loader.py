#!/usr/bin/env python3
"""AI PROJECT OS Context Loader — deterministic, read-only project context discovery."""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

EXCLUDES = {".git",".next","node_modules","dist","build","coverage",".venv","venv",
            "__pycache__",".pytest_cache",".mypy_cache",".ruff_cache",".idea",".vscode"}
BINARY = {".png",".jpg",".jpeg",".gif",".webp",".ico",".pdf",".zip",".gz",".tar",".mp4",
          ".mov",".avi",".mp3",".wav",".woff",".woff2",".ttf",".otf",".exe",".dll",".so",
          ".dylib",".bin",".sqlite",".db"}
SECRET = [r"\.env($|\.)", r"(^|/)(secrets?|credentials?)(/|\.|$)",
          r"(^|/).*?(secret|credential).*?\.(json|ya?ml|toml|ini|txt)$"]
ALWAYS = {"AGENTS.md","GEMINI.md","CLAUDE.md","SYSTEM.md",
          ".antigravity/GEMINI_DIRECTOR.md",".antigravity/AI_PROJECT_OS.md",
          ".antigravity/AI_PROJECT_OS_INTEGRATION.md",".antigravity/CAPABILITY_LEDGER.md"}
SIGNALS = {
 "architecture":["architecture","system design","adr","module","service","boundary"],
 "api":["api","endpoint","openapi","swagger","route","webhook","contract"],
 "database":["database","db","postgres","postgresql","supabase","sql","migration","schema","rls"],
 "ai":["ai","llm","gemini","openrouter","qwen","rag","embedding","agent","prompt","vector","model"],
 "frontend":["frontend","ui","ux","react","nextjs","component","page","css","tailwind","figma"],
 "backend":["backend","fastapi","python","handler","worker","queue","redis","service"],
 "testing":["test","pytest","playwright","vitest","jest","qa","quality"],
 "security":["security","auth","authorization","authentication","tenant","rls","permission","secret","payment"],
 "seo":["seo","sitemap","robots","canonical","schema.org","metadata","open graph"],
 "deployment":["deploy","docker","compose","vercel","ci","cd","production","release"],
 "docs":["readme","documentation","docs","spec","prd","adr","guide"]}

def norm(s): return re.sub(r"[^a-z0-9а-яё]+"," ",s.lower()).strip()
def secret(p, root):
    rel=str(p.relative_to(root)).replace("\\","/")
    return any(re.search(x,rel,re.I) for x in SECRET)
def digest(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()

def score(p, root, task):
    rel=str(p.relative_to(root)).replace("\\","/")
    n=norm(rel); t=norm(task); s=1000 if rel in ALWAYS else 0
    reasons=["always-context"] if rel in ALWAYS else []
    for domain,terms in SIGNALS.items():
        hits=[x for x in terms if x in t and x in n]
        if hits: s += min(80,20*len(hits)); reasons.append(f"{domain}:{','.join(hits[:3])}")
    overlap=set(t.split()) & set(n.split())
    if overlap: s += min(60,10*len(overlap)); reasons.append("token-overlap")
    if p.name.lower() in {"readme.md","package.json","pyproject.toml","docker-compose.yml","docker-compose.yaml"}:
        s += 15; reasons.append("project-metadata")
    return s,reasons

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("task"); ap.add_argument("--root",default="."); ap.add_argument("--top-k",type=int,default=30)
    ap.add_argument("--max-file-bytes",type=int,default=300000); ap.add_argument("--json",action="store_true")
    ap.add_argument("--write",default="")
    a=ap.parse_args(); root=Path(a.root).resolve(); rows=[]; skipped={"secret":0,"binary":0,"excluded":0,"oversize":0}
    for p in root.rglob("*"):
        if not p.is_file(): continue
        if any(x in EXCLUDES for x in p.parts): skipped["excluded"]+=1; continue
        if secret(p,root): skipped["secret"]+=1; continue
        if p.suffix.lower() in BINARY: skipped["binary"]+=1; continue
        size=p.stat().st_size
        if size>a.max_file_bytes: skipped["oversize"]+=1; continue
        s,r=score(p,root,a.task)
        if s: rows.append((s,str(p.relative_to(root)).replace("\\","/"),size,r))
    rows.sort(key=lambda x:(-x[0],x[1])); rows=rows[:a.top_k]
    m={"schema_version":"1.0","task":a.task,"project_root":str(root),
       "selection":{"top_k":a.top_k,"max_file_bytes":a.max_file_bytes,
                    "method":"deterministic lexical relevance scoring"},
       "context":[{"path":rel,"score":s,"size_bytes":z,"reasons":r,"sha256":digest(root/rel)}
                  for s,rel,z,r in rows],
       "skipped":skipped,"counts":{"candidates_scored":len(rows),"selected":len(rows)},
       "safety":{"source_files_modified":False,"secret_files_included":False,"binary_files_included":False}}
    data=json.dumps(m,ensure_ascii=False,indent=2)
    if a.write:
        q=Path(a.write); q.parent.mkdir(parents=True,exist_ok=True); q.write_text(data+"\n",encoding="utf-8")
        print(f"Context manifest written to {a.write}")
    else: print(data)
if __name__=="__main__": main()
