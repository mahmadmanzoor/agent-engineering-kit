#!/usr/bin/env bash
# Shared helpers. Source this file; do not run it.

# Print the shell command from the PreToolUse JSON on stdin.
# Prints nothing when the payload cannot be read.
read_command() {
  if command -v python3 >/dev/null 2>&1; then
    python3 -c '
import json, sys
try:
    print(json.load(sys.stdin).get("tool_input", {}).get("command", ""))
except Exception:
    print("")'
  elif command -v jq >/dev/null 2>&1; then
    jq -r '.tool_input.command // ""' 2>/dev/null
  else
    echo "guard: need python3 or jq to read the command; hook skipped" >&2
  fi
}

# Print the session's working directory ("cwd") from the PreToolUse JSON on stdin.
# Prints nothing when the payload has none.
read_cwd() {
  if command -v python3 >/dev/null 2>&1; then
    python3 -c '
import json, sys
try:
    print(json.load(sys.stdin).get("cwd", "") or "")
except Exception:
    print("")'
  elif command -v jq >/dev/null 2>&1; then
    jq -r '.cwd // ""' 2>/dev/null
  fi
}

# True when the command text contains a git commit.
is_commit() {
  case "$1" in
    *"git commit"*) return 0 ;;
    *) return 1 ;;
  esac
}
