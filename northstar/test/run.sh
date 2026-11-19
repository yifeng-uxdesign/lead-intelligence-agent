#!/usr/bin/env bash
# usage: northstar/test/run.sh        (no dependencies: Node's built-in test runner)
# Node needs ESM, so the widget is copied to a throwaway folder with a package.json; the widget itself is never modified.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; WIDGET="$(dirname "$HERE")"
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
cp -r "$WIDGET"/. "$TMP"; echo '{"type":"module"}' > "$TMP/package.json"
node --test "$TMP"/test/*.test.mjs
