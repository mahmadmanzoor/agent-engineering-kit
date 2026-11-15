# guard

Two opt-in hooks for Claude Code. Both run before a Bash command and only act on `git commit`.

## What they block

| Script | Blocks |
|---|---|
| `scripts/block-secret-commit.sh` | A commit whose staged, unstaged or untracked changes add a likely secret: private keys, cloud keys, service-account JSON, common API tokens. It prints file names only, never the value. |
| `scripts/block-main-commit.sh` | A commit made while the branch is `main` or `master`. |

A blocked commit exits with code 2 and a message on stderr.

## Overrides

- Secrets: no override. Move the value to config or the environment and commit placeholders. If the file should not be committed, add it to `.gitignore`.
- Main branch: allow one commit with `GUARD_ALLOW_MAIN=1 git commit -m "..."`. You can also set `GUARD_ALLOW_MAIN=1` in the agent's environment.

## Turn off

Disable the plugin (`/plugin`), or remove one hook entry from `hooks/hooks.json`.

## Needs

`bash`, `git`, and `python3` or `jq` to read the command from the hook input. Outside Claude Code you can run the scripts as git hooks.
