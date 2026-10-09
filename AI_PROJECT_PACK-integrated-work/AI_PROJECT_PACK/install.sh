#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET=""; MODE="install"; DRY=0; FORCE=0; YES=0; ALL=0; PLATFORMS=""
usage() {
  cat <<'HELP'
Usage: install.sh --target PATH [--all|--platform NAME,...] [--check|--update] [--merge] [--yes] [--dry-run] [--force]
  --target DIR       Target project directory
  --platform NAME    Install one adapter (comma-separated values allowed)
  --all              Install canonical files and all supported adapters
  --check            Report missing/outdated/conflicting managed files; no writes
  --update           Update managed files safely
  --merge            Interactive update/keep/diff/skip mode
  --yes              Confirm updates non-interactively; replaced files are backed up
  --dry-run          Show actions without writing
  --force            Force update of files without a detected upstream change
  --help             Show this help
HELP
}
while [ "$#" -gt 0 ]; do
  case "$1" in
    --target) TARGET="${2:-}"; shift 2;;
    --all) ALL=1; shift;;
    --platform) PLATFORMS="${2:-}"; shift 2;;
    --check) MODE="check"; shift;;
    --update) MODE="update"; shift;;
    --merge) MODE="merge"; shift;;
    --yes) YES=1; shift;;
    --dry-run) DRY=1; shift;;
    --force) FORCE=1; shift;;
    --help|-h) usage; exit 0;;
    *) usage >&2; exit 2;;
  esac
done
[ -n "$TARGET" ] || { usage >&2; exit 2; }
TARGET="$(cd "$TARGET" 2>/dev/null && pwd || { mkdir -p "$TARGET"; cd "$TARGET"; pwd; })"
STATE="$TARGET/.ai-pack/managed-files.tsv"
STALE=0
BACKUP="$TARGET/.ai-pack/backup/$(date +%Y%m%d_%H%M%S)"
log() { printf '[ai-pack] %s\n' "$*"; }
hash_file() { if command -v shasum >/dev/null 2>&1; then shasum -a 256 "$1" | awk '{print $1}'; else sha256sum "$1" | awk '{print $1}'; fi; }
source_hash() { local src="$1" rel="$2" h=""; if [ -f "$ROOT/source-hashes.tsv" ]; then h=$(awk -F '\t' -v p="$rel" '$1==p {print $2; exit}' "$ROOT/source-hashes.tsv"); [ -n "$h" ] && { printf "%s" "$h"; return; }; fi; hash_file "$src"; }
old_hash() { [ -f "$STATE" ] || return 0; awk -F '\t' -v p="$1" '$1==p {print $2; exit}' "$STATE"; }
record_hash() { [ "$DRY" -eq 1 ] || [ "$MODE" = "check" ] || printf "%s\t%s\n" "$1" "$2" >> "$STATE.tmp"; }
prepare_state() { [ "$DRY" -eq 1 ] || [ "$MODE" = "check" ] || { mkdir -p "$TARGET/.ai-pack"; : > "$STATE.tmp"; }; }
finish_state() { [ "$DRY" -eq 1 ] || [ "$MODE" = "check" ] || { mv "$STATE.tmp" "$STATE"; }; }
install_one() {
  local src="$1" rel="$2" dst="$TARGET/$2" new old current choice
  new="$(source_hash "$src" "$rel")"; old="$(old_hash "$rel")"; current=""
  [ -f "$dst" ] && current="$(hash_file "$dst")"
  if [ -z "$current" ]; then
    if [ "$MODE" = "check" ]; then STALE=1; log "MISSING $rel"; return 0; fi
    [ "$DRY" -eq 1 ] || { mkdir -p "$(dirname "$dst")"; cp "$src" "$dst"; }
    log "COPY $rel"; record_hash "$rel" "$new"; return 0
  fi
  if [ "$current" = "$new" ]; then log "UP-TO-DATE $rel"; record_hash "$rel" "$new"; return 0; fi
  if [ "$MODE" = "check" ]; then
    STALE=1
    if [ -n "$old" ] && [ "$current" = "$old" ]; then log "OUTDATED $rel (safe update available)"; else log "CONFLICT $rel (local changes detected)"; fi
    return 0
  fi
  if [ "$MODE" = "merge" ] || { [ "$MODE" = "update" ] && [ "$YES" -ne 1 ]; }; then
    if [ "$YES" -eq 1 ]; then choice="update"; else
      printf '[ai-pack] %s: update, keep, diff, or skip? [u/k/d/s] ' "$rel" >&2; read -r choice || choice="skip"
      case "$choice" in u|U) choice="update";; k|K|s|S) choice="skip";; d|D) diff -u "$dst" "$src" || true; printf 'Apply update? [y/N] ' >&2; read -r ans || ans="N"; [ "$ans" = "y" ] || [ "$ans" = "Y" ] && choice="update" || choice="skip";; *) choice="skip";; esac
    fi
  elif [ "$FORCE" -eq 1 ]; then choice="update"; else choice="skip"; fi
  if [ "$choice" = "update" ]; then
    if [ "$DRY" -eq 0 ]; then mkdir -p "$BACKUP/$(dirname "$rel")"; cp "$dst" "$BACKUP/$rel"; cp "$src" "$dst"; fi
    log "UPDATE $rel"; record_hash "$rel" "$new"
  else
    log "KEEP local: $rel"; record_hash "$rel" "$current"
  fi
}
copy_tree() {
  local base="$1" src
  while IFS= read -r src; do install_one "$src" "${src#"$ROOT/$base/"}"; done < <(find "$ROOT/$base" -type f -not -path '*/.DS_Store')
}
copy_tree_prefixed() {
  local base="$1" prefix="$2" src
  while IFS= read -r src; do install_one "$src" "$prefix/${src#"$ROOT/$base/"}"; done < <(find "$ROOT/$base" -type f -not -path '*/.DS_Store')
}
snapshot_source() {
  find "$ROOT/source" -type f -not -path '*/.DS_Store' -exec shasum -a 256 {} + | awk -v root="$ROOT/source/" '{p=$2; sub(root,"",p); print p "\t" $1}' >> "$STATE.tmp"
}
if [ "$ALL" -eq 1 ]; then PLATFORMS="antigravity,claude,cline,kilocode,continue,vscode,opencode,codex,ollama,hermes,koda,grok,qwen,kimi-code,minimax-agent,codegpt"; fi
[ -n "$PLATFORMS" ] || log 'No platform adapter selected; canonical files only.'
prepare_state
project_empty=1
for item in "$TARGET"/* "$TARGET"/.[!.]* "$TARGET"/..?*; do [ -e "$item" ] || continue; [ "$(basename "$item")" = ".ai-pack" ] && continue; project_empty=0; break; done
if [ "$MODE" = "install" ] && [ ! -f "$STATE" ] && [ "$project_empty" -eq 1 ] && [ "$DRY" -eq 0 ]; then
  tar -cf - -C "$ROOT/source" . | tar -xf - -C "$TARGET"
  snapshot_source
else
  copy_tree source
fi
IFS=',' read -r -a selected <<< "$PLATFORMS"
for platform in "${selected[@]}"; do
  case "$platform" in
    antigravity) copy_tree adapters/antigravity;;
    claude) copy_tree adapters/claude;;
    cline) copy_tree adapters/cline;;
    kilocode) copy_tree adapters/kilocode;;
    continue) copy_tree adapters/continue;;
    vscode) copy_tree adapters/vscode;;
    opencode) install_one "$ROOT/adapters/opencode/opencode.json.template" "opencode.json";;
    codex) log 'Codex uses canonical root AGENTS.md.';;
    ollama|hermes|koda|grok|qwen|kimi-code|minimax-agent|codegpt) copy_tree_prefixed "adapters/fallback/$platform" ".$platform";;
    '') ;;
    *) log "WARN unknown platform adapter: $platform";;
  esac
done
if [ "$DRY" -eq 0 ]; then
  mkdir -p "$TARGET/.ai-pack"
  finish_state
  printf '{"pack_version":"1.0.0","installed_at":"%s","platforms":"%s"}\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$PLATFORMS" > "$TARGET/.ai-pack/installation.json"
else
  log 'DRY-RUN complete; no files changed.'
fi
if [ "$MODE" = "check" ] && [ "$STALE" -ne 0 ]; then exit 1; fi
log "Done ($MODE). Review conflicts and fill PROJECT_STATUS.md before work."
