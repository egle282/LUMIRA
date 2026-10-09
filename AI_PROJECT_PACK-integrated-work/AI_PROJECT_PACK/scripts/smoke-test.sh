#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
fail=0
required=(platform-manifest.json README.md install.sh source/AGENTS.md source/SECURITY.md source/PROJECT_STATUS.md source/PACK_MANIFEST.md)
for file in "${required[@]}"; do
  if [ ! -s "$file" ]; then echo "FAIL missing: $file" >&2; fail=1; fi
done
if command -v jq >/dev/null 2>&1; then jq empty platform-manifest.json || fail=1; jq empty adapters/kilocode/kilo.jsonc || fail=1; jq empty adapters/vscode/.vscode/settings.json || fail=1; else echo 'WARN jq unavailable' >&2; fi
bash -n install.sh || fail=1
python3 -m py_compile source/reff_linter.py || fail=1
while IFS= read -r file; do bash -n "$file" || fail=1; done < <(find source scripts -type f -name '*.sh' -print)
if grep -RInE -- 'BEGIN (RSA |OPENSSH )?PRIVATE KEY|AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{20,}|gh[pousr]_[A-Za-z0-9]{20,}' . --exclude-dir=.git 2>/dev/null; then echo 'FAIL secret-like value found' >&2; fail=1; fi
if grep -RInE -- '--dangerously-allow-all|--dangerously-skip-permissions|--Autoerously' adapters source/.claude source/.antigravity 2>/dev/null; then echo 'FAIL dangerous bypass flag found' >&2; fail=1; fi
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
./install.sh --target "$TMP/project" --all --dry-run >/tmp/ai_pack_dry_run.log
[ -s /tmp/ai_pack_dry_run.log ] || fail=1
if [ "$fail" -ne 0 ]; then echo 'AI PACK SMOKE TEST: FAIL' >&2; exit 1; fi
echo 'AI PACK SMOKE TEST: PASS'
