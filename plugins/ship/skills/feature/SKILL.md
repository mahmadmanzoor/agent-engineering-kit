---
name: feature
description: "Carry one feature from idea to merged pull requests, one vertical slice at a time, by chaining the other ship skills with a gate after each step. Research, size, spec and plan review, epic and issues, docs PR, then per slice: branch, slice plan review, test-first build, commit check, PR, independent code review, CI, deploy check, merge gates. The one-command entry point. Use when someone wants a whole feature built. Say: '/ship:feature', 'build the X feature', 'implement X end to end', 'ship a whole feature', 'idea to PR'."
argument-hint: "[feature name | MVP id | design frame]"
license: MIT
metadata:
  version: "1.0.0"
  model: opus
  effort: medium
---

# Feature

Carry the feature in `$ARGUMENTS` (named by title, MVP id such as `B2`, or design frame) from first idea to merged slices. This skill only routes work. The rules for each step belong to the skill it hands off to. No argument: ask which feature.

**Run on:** opus at medium. It decides sizing and judges every gate.

## Use it when
- A feature needs research, a plan and more than one step to ship.
- You want one entry point instead of calling each skill by hand.

**Not for:** a single bug (`/ship:debug` then `/ship:fix-bug`), a repo with no rules yet (`/ship:new-repo`), or a raw idea (`/ship:idea-brief`).

## Before you start
Read `AGENTS.md`: tracker, milestones, commands, merge gates, optional policies, the safety-critical list. If the repo has no `AGENTS.md`, no conventions and no CI, offer `/ship:new-repo` first. Agents copy whatever the first file does.

Solo developer? Say "just build it" for a small change. That skips the issue and epic steps (3 and 4 below). The plan review and the test-first rules still apply whenever the code is risky.

## Steps
1. **Research.** Make the docs issue, then run `/ship:feature-research`. Skip if a build pack exists.
   **Stop if:** open product questions remain. They belong to the owner.
2. **Size it.** The feature is non-trivial if any of these is true:
   - It touches two or more of client, platform, server, data.
   - It adds or changes a table, a scheduled job, notifications or uploads.
   - It touches a path on the safety-critical list.
   - It changes who can see whose data.
   - The build pack has an unresolved product question.
3. **Spec or one issue.**
   - Non-trivial: `/ship:write-spec` (with its plan review on the epic), then `/ship:spec-to-issues`, then `/ship:open-pr` for the docs.
   - Small: `/ship:file-issue`, then the docs PR.
   **Stop if:** the owner has not approved the breakdown. No issue exists before approval.
4. **Start a slice.** After the docs PR merges, run `/ship:start-issue` on the riskiest slice.
5. **Slice plan review.** `/ship:plan-review`, posted on the slice issue.
   **Stop if:** the review is not posted or a finding is open. This step is never skipped, not for speed, not for small slices.
6. **Build.** `/ship:build`, test-first, following the review.
   **Stop if:** an acceptance criterion has no evidence.
7. **Ship the slice.** `/ship:commit-check`, `/ship:open-pr`, then an independent review by `crew:code-reviewer` posted on the PR.
8. **Prove it.** `/ship:ci-green`, `/ship:deploy-check`, and `/mobile:device-test` when the change is device-relevant.
9. **Merge.** `/ship:merge-gates`. Then go back to step 4 for the next slice.

## Done when
- [ ] Every slice is merged, one branch and one PR each.
- [ ] Each slice has a posted plan review dated before its first production commit.
- [ ] Each acceptance criterion has evidence (command and output).
- [ ] The merge gates held. Green tests alone do not count.

## Never
- Write production code before the issue exists in its milestone.
- Stack several slices in one PR.
- Reorder slices without the owner. The filed order puts the riskiest first.
- Cut tests, the plan review or the code review for speed. Speed may trim reruns and review rounds only. Say this in every brief to a subagent.

## Next
- **Comes from:** `idea-brief`, `new-repo` (ship), the owner
- **Leads to:** `release` (ship) when the milestone ships
