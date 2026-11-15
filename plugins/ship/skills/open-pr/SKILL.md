---
name: open-pr
description: "Open a pull request that a reviewer can trust. Reuses an existing PR, insists the PR close an issue, syncs the branch with main, gathers real evidence before writing anything, describes the change area by area with safety notes, pushes on the user's go-ahead, then gets an independent review posted on the PR and clears critical and major findings ahead of CI and merge. Use when a branch has reached review stage. Say: 'raise a PR', 'send this for review', 'open a PR', '/ship:open-pr', 'create the pull request', 'push and open a PR'."
argument-hint: "[issue #, branch, or --draft]"
license: MIT
metadata:
  version: "1.0.0"
  model: sonnet
  effort: medium
---

# Open PR

Make a PR from the current branch, or from whatever `$ARGUMENTS` names: a branch name, `--draft`, or an issue number to link.

**Run on:** sonnet at medium. The work is structured writing backed by checkable evidence.

## Use it when
- The branch is committed and ready for review.
- A PR is already open and its text or review is out of date.

**Not for:** committing (`commit-check`) or merging (`merge-gates`).

## Before you start
Read AGENTS.md, CONTRIBUTING.md and the PR template (`.github/pull_request_template.md`, or the tracker's version). Note:
- Which tracker and CLI to use. `gh` for GitHub is the example here; the project's own wins.
- Label set, milestones, base branch.
- The merge gates, owned by `merge-gates`.
- Whether pushing or opening a PR needs the user's go-ahead.
- The rules on authorship and attribution in PR text.

## Steps
1. **Check the starting state.**
   ```bash
   BRANCH=$(git rev-parse --abbrev-ref HEAD); echo "$BRANCH"
   git status -sb
   git fetch origin && git log origin/main..HEAD --oneline
   gh pr list --head "$BRANCH"
   ```
   If this branch has a PR already, push to it and edit it. Do not open another.
   **Stop if:** you are on the main branch, or the working tree has uncommitted changes (run `commit-check` first).
2. **Tie it to an issue.** Every PR closes one. Read it off the branch name, or search the tracker. Start the body with `Closes #<issue>`, one line per issue. Copy the issue's labels onto the PR, except workflow labels such as in-progress and blocked. Copy its milestone. Add an area label for each area the diff touches.
   **Stop if:** no issue exists. Create it with `file-issue` or `file-bug`, then carry on.
3. **Sync with main.**
   ```bash
   git rebase origin/main
   ```
   If the branch was already pushed and reviewed, merge main in instead. Resolve conflicts, then re-run any `commit-check` step they touch. Then audit each commit's author and message for policy breaches: `git log --format='%an <%ae> %s' origin/main..HEAD`.
   **Stop if:** it needs a force-push and the user has not agreed. On a feature branch use `--force-with-lease`. Never force-push the main branch.
4. **Gather the evidence first.** Use real output. "Tests pass" proves nothing alone.
   - Lint, test and build results for each changed area, with counts.
   - Screenshots of the screens you changed. Synthetic data only.
   - The plan review link from the issue (`plan-review`), and one line on how the diff follows it.
   - Real-device runs (`device-test`, mobile plugin), when the change touches background work, notifications, widgets or battery. If they are not run yet, list them as open. Some projects batch them before release, and AGENTS.md says so.
   - Performance figures (`perf-check`, check plugin) when a budget applies.
   **Stop if:** you are about to state something you cannot back up.
5. **Write the description.** Use the project template. With none, use the layout below. A reader should learn, area by area, what changed and why, without opening the diff.
   ```markdown
   ## Summary
   Closes #<issue>

   <Two lines at most: what the user gets, and why.>

   ## Changes by area
   - [x] **Server** (3 files): the booking overlap check now lives in the domain, shared by all entry points.
   - [x] **Mobile client** (5 files): the booking form shows the overlap error.
   - [ ] **Web client**
   - [ ] **Infra and CI**
   - [ ] **Docs**

   ## Acceptance
   - [x] <issue criterion>, checked by <how>
   - [ ] <criterion still open>, because <why> (drafts only)

   ## Testing
   - [x] `<test command>` gave 58 passed
   - [ ] Skipped: <what, and why>

   ## Plan review
   <link>. Followed, or what differs and why.

   ## Review
   - [ ] Posted, covers the head commit, no critical or major finding open

   ## Failure modes and data
   Cases weighed (offline, retry, duplicate, crash midway, permission revoked), each with its test. Which personal data goes where. Put "None" only if nothing relevant changed.

   ## Screens
   Before and after, synthetic data.
   ```
   Unticked areas stay in the list, since they record what was left alone. Tick more as later commits reach new areas. Write the body to a scratch file and pass the file, never inline text. If the project forbids AI mentions, run `grep -niE 'co-authored-by|generated with' <body-file>`, which must print nothing.
6. **Push and open, with the go-ahead.** First show the user the title, labels and description. Skip the check only when the user's request told you to open it.
   ```bash
   git push --set-upstream origin HEAD
   gh pr create --head "$BRANCH" --base main --title "<conventional title>" \
     --body-file <body-file> --label "<issue labels>" --milestone "<milestone>" [--draft]
   ```
7. **Get an independent review.** It comes after the PR is open so everyone can see it. The reviewer posts it, not you.
   1. Start the `crew:code-reviewer` agent with the PR link and nothing else. It starts fresh and cannot see this conversation.
   2. It runs `review-code` (check plugin). If the change involves analytics, payments, uploads, sharing, auth or personal data, it also runs `security-review` and posts `## Security & privacy review — <SHA>`.
   3. It posts one comment opening with `## Code review — <short head SHA>`. When it has no way to post, it hands the text back and you post it unchanged.
   4. You only verify the comment is there and names the current head SHA.
   5. Resolve each critical and major finding. The one exception is a finding the user explicitly chose to defer, noted in the PR. Push. Then a fresh reviewer posts `## Code review — <new SHA> (re-review)` for the new commits.
   6. Minor findings and nits get fixed or answered in that re-review.
   **Stop if:** the newest review misses the head commit, or a critical or major finding is still open.
8. **Pass it on.** Run `ci-green`. Then `deploy-check` when the diff reaches schedulers, config, platform code, data or an API. Then `merge-gates`. Ask no human reviewers unless the project says to.

## Done when
- [ ] One PR exists for the branch, and it closes an issue.
- [ ] Every claim in the description is backed by evidence.
- [ ] The newest review comment names the head SHA, and nothing critical or major is open.
- [ ] Your report lists the PR link, CI per job, the review verdict, and open items.

## Never
- Let unrelated changes ride along. Each branch and PR serves one issue.
- Claim a check you never ran. Report these as distinct: implemented, verified, PR open, CI green, merged, released.
- Let the author double as the independent reviewer.
- Force-push, or push to another person's branch, without a separate OK.
- Push or open the PR before the go-ahead, when the project requires one.

## Next
- **Comes from:** `build`, `fix-bug`, `commit-check` (ship)
- **Leads to:** `ci-green`, then `deploy-check`, then `merge-gates` (ship)
