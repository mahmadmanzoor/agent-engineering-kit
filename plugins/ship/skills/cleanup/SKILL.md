---
name: cleanup
description: "Clean up once a pull request is merged or dropped. Verify the PR's state, update the issue and epic checklist, delete branches (local and remote), remove the worktree from a different checkout, and stop whatever services, emulators and dev servers this work started. Other projects' services and any shared stash stay untouched. Use after a merge, or for an abandoned branch. Say: '/ship:cleanup', 'tidy up', 'it merged, clean up', 'drop the worktree', 'remove the branch', 'shut down the services'."
argument-hint: "[PR or branch]"
license: MIT
metadata:
  version: "1.0.0"
  model: haiku
  effort: low
---

# Cleanup

Clear away what the work on `$ARGUMENTS` left behind. It takes a PR or branch, and defaults to the current branch.

**Run on:** haiku at low. Each step is mechanical and its result is easy to check.

## Use it when
- Your PR just merged.
- A branch is abandoned and you want it removed.

**Not for:** the merge itself (use `merge-gates`).

## Before you start
Read AGENTS.md for four facts: the tracker and its CLI, where worktrees are kept, how local services start and stop (compose file or scripts), and whether the remote removes merged branches on its own.

## Steps
1. **Check what state the work is in.**
   ```bash
   gh pr view <PR|branch> --json number,state,mergedAt,headRefName,closingIssuesReferences
   ```
   - Merged: go on.
   - Still open: stop. Nothing is ready to clean.
   - Closed unmerged: ask if the work is abandoned before deleting anything. Deleting the branch destroys unmerged commits.

   **Stop if:** the PR is unmerged and the user has not said the work is abandoned.
2. **Update the tracker.** This edits a shared board, so ask once for the whole batch.
   - `Closes #<issue>` in the PR closes the issue by itself. If it did not, close the issue and comment with the PR.
   - Drop workflow labels such as in-progress.
   - If it was a sub-issue, look at its siblings in the epic. If all are closed, tell the user the epic may close and the spec may be marked shipped.
3. **Clean up git.**
   ```bash
   git fetch --prune origin
   git worktree list
   ```
   - The branch checked out in your current worktree cannot be deleted. Step off it first: `git switch --detach origin/main`.
   - Delete locally with `git branch -d <branch>`. It refuses unmerged work. A squash merge looks unmerged to git, so confirm on the PR that it merged. Only then, and only with the user's OK, use `-D`.
   - To remove a worktree, run the command from another checkout: `git -C <main checkout> worktree remove <path>`. Uncommitted changes make it refuse. Ask the user at that point.
   - Delete the remote branch only when the host has not already done so, and only with the user's OK: `git push origin --delete <branch>`.

   **Stop if:** a branch or worktree holds uncommitted or unmerged work and the user has not agreed to lose it.
4. **Stop local services.** Shut down what this work started and nobody needs now. If you cannot tell who started something, ask first.
   - The project's local services. Keep their data volumes. Remove volumes only if the user asks.
   - Emulators, simulators, dev servers and background test runners from this session.

## Done when
- [ ] The PR is confirmed merged, or abandonment is confirmed.
- [ ] The issue and the epic checklist are current.
- [ ] The local branch, the remote branch and the worktree are removed, or deliberately kept.
- [ ] Services started for this work are stopped.

Report what was closed, deleted and stopped, plus anything you left on purpose.

## Never
- Delete anything unmerged unless the user agrees.
- Force-delete, prune volumes, or reset a branch another person may rely on.
- Stash in a repository shared by worktrees or sessions: they all see the same stash. Commit or discard, with the user's OK.
- Touch containers, services or volumes that belong to other projects on the machine.

## Next
- **Comes from:** `merge-gates` (ship)
- **Leads to:** `start-issue` (ship), for the next issue
