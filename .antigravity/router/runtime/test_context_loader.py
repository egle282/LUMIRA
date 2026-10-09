import json, subprocess, sys
from pathlib import Path
def test_excludes_secrets(tmp_path):
    (tmp_path/"src").mkdir()
    (tmp_path/".env").write_text("SECRET=x")
    (tmp_path/"src"/"rag.py").write_text("tenant isolation rag")
    script=Path(__file__).with_name("context_loader.py")
    p=subprocess.run([sys.executable,str(script),"--json","--root",str(tmp_path),"RAG tenant isolation"],
                     capture_output=True,text=True)
    assert p.returncode==0
    d=json.loads(p.stdout)
    paths=[x["path"] for x in d["context"]]
    assert "src/rag.py" in paths and ".env" not in paths
    assert d["safety"]["secret_files_included"] is False
