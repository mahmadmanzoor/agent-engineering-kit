#!/usr/bin/env bash
# Put this kit's skills into a flat skills folder, for agents that read SKILL.md folders
# (Codex, Cursor, Gemini CLI, Copilot) instead of Claude Code plugins.
#
#   scripts/install-skills.sh <skills-dir> [--link] [--only ship,check,web]
#
#   scripts/install-skills.sh ./.agents/skills                 # copy every skill
#   scripts/install-skills.sh ~/.codex/skills --link            # symlink, stays in sync with this clone
#   scripts/install-skills.sh .cursor/skills --only ship,check  # just some plugins
set -euo pipefail

kit="$(cd "$(dirname "$0")/.." && pwd)"
dest_root="${1:?usage: install-skills.sh <skills-dir> [--link] [--only a,b]}"
shift

link=0
only=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --link) link=1 ;;
    --only) only="${2:?--only needs a comma list}"; shift ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done

mkdir -p "$dest_root"
done_count=0
for dir in "$kit"/plugins/*/skills/*/; do
  dir="${dir%/}"
  plugin="$(basename "$(dirname "$(dirname "$dir")")")"
  [ -n "$only" ] && [[ ",$only," != *",$plugin,"* ]] && continue
  skill="$(basename "$dir")"
  dest="$dest_root/$skill"
  if [ -e "$dest" ] && [ ! -L "$dest" ]; then
    echo "skip $skill: $dest already exists and is not a link from this kit"
    continue
  fi
  rm -f "$dest"
  if [ "$link" -eq 1 ]; then ln -s "$dir" "$dest"; else cp -R "$dir" "$dest"; fi
  done_count=$((done_count + 1))
done

echo "$([ "$link" -eq 1 ] && echo linked || echo copied) $done_count skills into $dest_root"
echo "Review agents live in plugins/crew/agents/. See docs/other-agents.md for tools without subagents."
