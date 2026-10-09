#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
find source -type f -not -path '*/.DS_Store' -exec shasum -a 256 {} + | awk '{p=$2; sub(/^source\//,"",p); print p "\t" $1}' > source-hashes.tsv
echo "Updated source-hashes.tsv"
