#!/usr/bin/env bash
# PreToolUse hook for Bash.
# Blocks "git commit" while the current branch is main or master.
# Work goes on a branch and lands through a pull request.
#
# To allow one commit (for example the first commit in a new repo), either:
#   - put the flag in the command:  GUARD_ALLOW_MAIN=1 git commit -m "chore: initial commit"
#   - or start the agent with GUARD_ALLOW_MAIN=1 in its environment.
# The hook runs before the command does, so a prefix never reaches this
# script's environment. That is why the command text is checked below.

# shellcheck source=common.sh
. "$(dirname "$0")/common.sh"

[ "${GUARD_ALLOW_MAIN:-}" = "1" ] && exit 0

cmd="$(read_command)"
is_commit "$cmd" || exit 0

flag_re='(^|[;&|[:space:]])(export[[:space:]]+)?GUARD_ALLOW_MAIN=1([;&|[:space:]]|$)'
printf '%s' "$cmd" | grep -qE "$flag_re" && exit 0

dir="${CLAUDE_PROJECT_DIR:-.}"
branch="$(git -C "$dir" branch --show-current 2>/dev/null || git branch --show-current 2>/dev/null)"

case "$branch" in
  main|master)
    {
      echo "Blocked: you are committing directly on '$branch'. Make a branch first (git switch -c <type>/<slug>)."
      echo "To allow one commit, add the flag to the command: GUARD_ALLOW_MAIN=1 git commit ..."
    } >&2
    exit 2 ;;
esac
exit 0
