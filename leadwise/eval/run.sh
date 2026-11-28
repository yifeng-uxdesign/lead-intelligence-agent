#!/usr/bin/env bash
# usage: leadwise/eval/run.sh > leadwise/eval/baseline-YYYY-MM-DD.md
# Node needs ESM, so run on a throwaway copy with a package.json (the widget itself is never modified).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; WIDGET="$(dirname "$HERE")"
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
cp -r "$WIDGET"/. "$TMP"; echo '{"type":"module"}' > "$TMP/package.json"
node "$HERE/run.mjs" "$TMP"
