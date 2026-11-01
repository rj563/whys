#!/usr/bin/env bash
# SessionStart hook: valid JSON, short context, works outside a git repo.
set -u
ROOT=$(cd "$(dirname "$0")/.." && pwd)
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
fail() { echo "FAIL: $1"; exit 1; }

out=$(cd "$TMP" && CLAUDE_PLUGIN_ROOT="$ROOT" "$ROOT/hooks/session-start") || fail "exit code $?"
ctx=$(printf '%s' "$out" | python3 -c 'import json,sys; print(json.load(sys.stdin)["hookSpecificOutput"]["additionalContext"])') || fail "invalid JSON: $out"
case "$ctx" in *whys:drill*) ;; *) fail "no whys:drill";; esac
case "$ctx" in *"skip whys"*) ;; *) fail "no skip whys";; esac
case "$ctx" in *whys:check*) ;; *) fail "no whys:check";; esac
bytes=$(printf '%s' "$ctx" | wc -c)
[ "$bytes" -le 600 ] || fail "context $bytes bytes > 600"
python3 -c 'import json,sys; h=json.load(open(sys.argv[1]))["hooks"]["SessionStart"][0]; assert "startup" in h["matcher"]' "$ROOT/hooks/hooks.json" || fail "hooks.json"
echo "PASS ($bytes bytes)"
