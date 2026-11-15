---
name: merge-gates
description: "Defines the eight gates a PR must pass, then merges it once they all hold. The gates: green CI on a head that includes current main, a posted code review with nothing critical or major open, a closing keyword for the issue, local runs of checks CI skips, a plan review posted before production code, a clean design pass, the merger reading the diff personally, and the deploy and privacy verdicts where they apply. Handles stacked PRs bottom-up. Use when a PR seems ready. Say: 'is this ready to merge', '/ship:merge-gates', 'can I merge', 'merge this', 'ship the PR', 'merge gates'."
argument-hint: "[PR]"
license: MIT
metadata:
  version: "1.0.0"
  model: opus
  effort: medium
---

# Merge gates

Look at the PR in `$ARGUMENTS` (default: the PR of the current branch), test it against the eight gates, and merge if all hold. If not, say which gate fails and what would fix it.

**Run on:** opus at medium. A bad merge is expensive, and the diff needs a careful read.

## Use it when
- A PR seems ready to go in.
- You need to know which gate is holding a PR back.

**Not for:** shipping to users (`release`). Merging and releasing are separate acts.

## Before you start
Read AGENTS.md, CLAUDE.md and CONTRIBUTING.md for:
- The merge policy: after the gates hold, may the agent merge alone, or does it ask? **Default: ask.** Follow the project's wording exactly.
- The merge method: merge commit, squash or rebase.
- The names of the required checks.
- Area checks that CI does not run.
- Extra project gates. They stack on top of the eight below and never replace one.

These policies count only when AGENTS.md states them: PR CI is off and local runs stand in; some checks run only on main; device tests wait for one batch pass before release; the agent may merge unasked. If AGENTS.md is silent, assume none.

## Steps
1. **Test each gate and collect proof.**
   ```bash
   gh pr view <PR> --json headRefOid,mergeStateStatus,statusCheckRollup
   gh pr view <PR> --json body,closingIssuesReferences
   gh pr view <PR> --comments
   gh issue view <issue> --comments
   gh pr diff <PR>
   ```
   | # | Gate | What counts |
   |---|---|---|
   | 1 | CI on the head, against current main | Every required check passes, or is skipped because nothing in its area changed. A PR that is behind main, or was just retargeted, pulls main in, pushes and waits for a new green run. Where policy turns PR CI off, the proof is a complete local run of the project's checks on the head, with its summary pasted in the PR. |
   | 2 | Code review of the head | The `crew:code-reviewer` agent posts it through `review-code` (check plugin). No `critical` or `major` finding open. Any commit after the reviewed one is a reviewed fix or has a re-review note. |
   | 3 | Issue closure | `Closes #<issue>` in the PR body. |
   | 4 | Area checks CI skips | Only if the project lists some. Run locally on the head, output pasted in the PR. |
   | 5 | Plan review first | For a feature or non-trivial fix (see `code-placement`): the issue holds a `plan-review` posted before the first commit of production code, with no finding open. A failing reproduction test or characterisation tests may come first. A slice of a specified feature also needs the epic's spec-level review. |
   | 6 | Design pass | The code review's design pass has no open `major` finding. |
   | 7 | Diff read | The merging session reads `gh pr diff <PR>` itself. Passing tests and a kind review do not replace this. Confirm the change does what the issue asks, nothing extra, and matches the plan review. |
   | 8 | Verdicts | `deploy-check` if the change touches API, data, platform code, config or scheduling. `security-review` (check plugin) if it touches payments, auth, sharing, uploads, analytics or personal data. No row flagged unsafe, no critical privacy finding open. The only exception is an owner's acceptance quoted in the PR. |

   Speed rule: you may drop test reruns and review rounds to go faster. You may not drop the tests that were written, the plan review or the design pass.
   **Stop if:** any gate has no evidence (a link, a SHA or command output). Repair it. Do not work around it.
2. **Merge.**
   1. If the policy is to ask, present the ticked gates and wait. If the agent may merge, go ahead.
   2. Run `gh pr merge <PR> --merge`, or use the project's method.
   3. Check that the issue closed. Tick the epic's checklist if one exists.
   4. Watch CI on main after the merge.
   **Stop if:** main turns red. Fix main before merging anything else.
3. **Stacked PRs.** Go from the bottom up. Once the bottom PR is in, retarget the next one at main (`gh pr edit <next> --base main`), pull main in, wait for a new green run and a review of the new head, then merge it. Repeat.
4. **Open device tests.** They block the merge, unless the project runs them in one real-device batch before release. Then mark them open in the PR and run `device-test` (mobile plugin) ahead of `release`. If it does not, they fall under gate 4.

## Done when
- [ ] Every one of the eight gates is ticked, each with proof.
- [ ] The PR is merged and the merge commit is noted.
- [ ] The state of main's CI after the merge is reported.
- [ ] Open items (device tests, follow-up issues) are listed.

Be exact about status. Implemented, verified, PR open, CI green, merged and released are six separate states.

## Never
- Skip a failing gate: no admin merge, no switched-off check, no "review later".
- Merge a PR written by someone else, or one from a fork, unless the user says yes.
- Release or deploy as a side effect of merging. Each keeps its own approval.

## Next
- **Comes from:** `ci-green`, `open-pr`, `deploy-check`, `plan-review` (ship); `security-review` (check)
- **Leads to:** `release`, `cleanup` (ship)
