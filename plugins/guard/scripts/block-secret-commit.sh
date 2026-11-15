#!/usr/bin/env bash
# PreToolUse hook for Bash.
# Blocks "git commit" when the change would add something that looks like a secret.
# It prints file names only. It never prints the matched value.
#
# What it scans:
#   - the staged diff
#   - unstaged edits to tracked files (a command like "git add . && git commit" stages them later)
#   - new untracked files
# Fix a false positive by moving the value into config or the environment.
# Example config files should hold placeholders only.

# shellcheck source=common.sh
. "$(dirname "$0")/common.sh"

cmd="$(read_command)"
is_commit "$cmd" || exit 0

# Patterns for private keys, cloud keys, service-account JSON and common API tokens.
secret_re='-----BEGIN ([A-Z ]+ )?PRIVATE KEY-----'
secret_re+='|AKIA[0-9A-Z]{16}'
secret_re+='|AIza[0-9A-Za-z_-]{35}'
secret_re+='|"private_key"[[:space:]]*:'
secret_re+='|xox[baprs]-[0-9A-Za-z-]{10,}'
secret_re+='|gh[pousr]_[0-9A-Za-z]{36}'
secret_re+='|github_pat_[0-9A-Za-z_]{40,}'
secret_re+='|sk_live_[0-9A-Za-z]{20,}'
secret_re+='|sk-[A-Za-z0-9_-]{32,}'

# List the files in a diff whose added lines match. Extra args go to "git diff".
diff_hits() {
  local current="" line
  while IFS= read -r line; do
    case "$line" in
      "+++ b/"*) current="${line#+++ b/}" ;;
      "+++ "*)   current="" ;;
      "+"*)
        if [ -n "$current" ] && printf '%s\n' "$line" | grep -qE -- "$secret_re"; then
          printf '%s\n' "$current"
        fi ;;
    esac
  done < <(git -c core.quotePath=false diff "$@" -U0 2>/dev/null)
}

untracked_hits() {
  git ls-files --others --exclude-standard -z 2>/dev/null \
    | xargs -0 grep -lE -- "$secret_re" 2>/dev/null
}

hits="$( { diff_hits --cached; diff_hits; untracked_hits; } | sort -u | head -10 )"

if [ -n "$hits" ]; then
  {
    echo "Blocked: these files look like they add a secret (key, token or service-account JSON)."
    echo "Move the value to config or the environment. Commit placeholders only."
    printf '%s\n' "$hits" | sed 's/^/  /'
    echo "If a file should never be committed, add it to .gitignore."
  } >&2
  exit 2
fi
exit 0
