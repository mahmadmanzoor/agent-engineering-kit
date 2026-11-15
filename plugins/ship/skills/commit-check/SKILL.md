---
name: commit-check
description: "Inspect the working tree, then commit it with care. Make sure you are off the main branch, stage explicit paths, search the staged diff for secrets and personal data, regenerate generated code, format just the files you touched, run lint and tests for each changed area, confirm safety-critical paths have failure tests, and write a conventional commit that obeys the project's author policy. Hooks are never bypassed. Use before every commit. Say: '/ship:commit-check', 'commit this', 'am I ready to commit', 'check then commit', 'stage this and commit'."
argument-hint: "[optional message or scope]"
license: MIT
metadata:
  version: "1.0.0"
  model: sonnet
  effort: low
---

# Commit check

Inspect the working tree, then commit `$ARGUMENTS` (a message or scope, both optional). Work through every step whose files changed. A step may be skipped only if none of its files changed, and the report must say so.

**Run on:** sonnet at low. Every step is mechanical and its result can be checked.

## Use it when
- You are about to commit.
- You are unsure the change is ready.

**Not for:** pushing or opening a PR (use `open-pr`).

## Before you start
Read AGENTS.md, CLAUDE.md and CONTRIBUTING.md and collect:
- the format, lint, test and build commands for each area
- the code generators
- the commit message convention
- the author policy: who commits, and whether AI co-author trailers or "generated with" footers may appear

Check which hooks already fire (in `.git/hooks`, a hook manager's config, or the agent's settings). Whatever they cover, you need not repeat. Missing fact: ask once, and offer to put the answer in AGENTS.md.

## Steps
1. **Check the branch and the tree.**
   ```bash
   git branch --show-current
   git status --short
   git diff --cached --stat
   git diff --stat
   ```
   **Stop if:** the branch is the main branch. Make a branch named the way `start-issue` names them, and carry the changes over.
2. **Stage explicit paths.** Name each path. `git add -A` and `git add .` are out. Exclude: compiled output, vendored dependencies, `.env*` files and other local config, keys, signing material, credentials, screenshots of real data, and scratch notes. If any of these is not yet ignored, fix `.gitignore` in its own commit.
   **Stop if:** `git diff --cached --name-only` shows a file that is not part of this change.
3. **Scan for secrets and personal data.**
   ```bash
   # keys and secrets
   git diff --cached -U0 | grep -nEi '(api[_-]?key|secret|password|passwd|token|BEGIN [A-Z ]*PRIVATE KEY)' || true
   # coordinates
   git diff --cached -U0 | grep -nE '[-+]?[0-9]{1,2}\.[0-9]{4,},\s*[-+]?[0-9]{1,3}\.[0-9]{4,}' || true
   # email addresses
   git diff --cached -U0 | grep -nEi '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}' || true
   ```
   Judge each hit by eye. A real secret gets unstaged and moved into configuration, and the user hears about it. Anything that was already pushed must be rotated. Personal data is allowed only as clearly fake fixtures. The `guard` plugin's hook catches common key shapes. It backs up this scan and does not replace it.
   **Stop if:** a real secret or real personal data is staged.
4. **Sync generated code.** For every source the diff touched, run the matching generator (commands live in AGENTS.md) and stage what it writes.
   - API contract: client and server stubs
   - string or translation files: generated text code
   - native bridge definitions: both sides of the bridge
   - annotated models: generated model files
   - database models: the migration (`add-migration`, server plugin)

   Generated files are never edited by hand.
   **Stop if:** a second generator run still produces a diff.
5. **Format, lint and test by area.** Run the formatter on hand-written files from this commit only. Then, per changed area, run the lint and tests named in AGENTS.md. Integration tests expect the project's local services to be up. Re-stage any file the formatter rewrote.
   **Stop if:** any command exits non-zero. Fix the cause. Do not bypass.
6. **Check safety-critical paths.** Use the project's list. Without one, a path is safety-critical when a quiet failure could harm a person, cost money or destroy data. If the diff touches such a path, a failure-path test must exist in this commit or an earlier commit on the branch (`test-rules`, check plugin). A catch block must never swallow an error: log it and surface it.
   **Stop if:** a safety-critical change has no failure-path test.
7. **Commit.** Write a conventional message in the imperative with a subject of 72 characters or fewer: `type(scope): summary`. Types: `feat fix refactor perf test docs build ci chore style`. Add a body that explains why when the reason is not obvious, and cite the issue with `Refs #<issue>`.
   ```bash
   git commit -m "feat(bookings): reject bookings of more than 8 guests" -m "Refs #<issue>"
   git log -1 --format='%an <%ae>%n%B'
   ```
   Follow the author and attribution policy to the letter. If it bans AI trailers or "generated with" lines, read the final message yourself. A hook that scans the command line cannot see a message loaded from a file.

## Done when
- [ ] You are not on the main branch.
- [ ] Only named paths that belong to the change were staged.
- [ ] The secret and personal-data scan has no real hit.
- [ ] Every format, lint and test command exited 0, and the output is kept.
- [ ] The commit exists, and its author and message match the policy.

Report each check with its result, anything skipped with the reason, and the commit hash.

## Never
- Use `--no-verify`, or disable a hook, to get a commit through.
- Put a refactor and a behaviour change in the same commit. One logical change per commit.
- Push from this skill. `open-pr` owns pushing.
- Stash when worktrees or sessions share the repository. Park unfinished work in a commit on its own branch.

## Next
- **Comes from:** `build`, `fix-bug` (ship), `test-first` (check)
- **Leads to:** `open-pr` (ship)
