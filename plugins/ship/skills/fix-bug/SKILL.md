---
name: fix-bug
description: "Repair a bug from start to finish. Reuse or run the investigation, review the plan when the fix is non-trivial, turn the reproduction into a permanent regression test that fails first for the reported reason, fix the root cause, add a guard against recurrence, then check what else the bug touches (same pattern, other platform, stored data, old installed versions), verify and open the PR. Use once a bug needs a fix. Say: '/ship:fix-bug', 'fix this bug', 'fix the issue', 'turn this test green', 'ship the fix', 'hotfix'."
argument-hint: "[bug issue | path to investigation report | description]"
license: MIT
metadata:
  version: "1.0.0"
  model: opus
  effort: medium
---

# Fix bug

Fix the bug in `$ARGUMENTS`, given as an issue, an investigation report or plain description. Nothing given: ask which bug.

**Run on:** opus at medium. A shallow fix leaves the real cause in place.

## Use it when
- The root cause is confirmed and a fix is due.
- A bug issue exists and you are ready to change code.

**Not for:** hunting the cause (use `debug`) or adding a missing capability (use `file-issue`, then `feature`).

## Before you start
Read AGENTS.md for commands, release paths, the safety-critical list and the merge gates (`merge-gates`). Then choose where to enter, based on what you hold:
- **A root cause from this conversation:** use it and skip re-investigating.
- **A bug issue without a root cause:** run `debug` first.
- **Only a description:** run `file-bug` first with the cause as "unknown", then `debug`. No issue means no fix.
- **A report that says "not reproduced" or "unverified":** stop and report what evidence is missing. Do not guess at a fix.

A bug counts as safety-critical if the project's list says so. By default that means a critical action missed or doubled, data exposed, lost or corrupted, or a background worker dead. Put that fact at the top of every reply, rate the bug P0 or P1, and require `device-test` in the PR when platform code is involved.

## Steps
1. **Plan review for a non-trivial fix.** A fix is non-trivial if it adds a type, file, dependency or rule, or touches more than one production file. Run `plan-review` and post the result on the bug issue ahead of the first production-code commit. A reproduction test may already be on the branch.
   Ask whether this whole class of bug needs one shared fix instead of a local patch. For a trivial fix, say in the PR why it is trivial.
   **Stop if:** a non-trivial fix has no posted plan review.
2. **Pick the branch.** Reuse the linked branch `debug` created. If there is none, run `start-issue` to get `fix/<n>-<slug>`.
   **Stop if:** you are on the main branch.
3. **Make the regression test permanent (RED).** Move the reproduction beside the related tests. Run it on unfixed code and read the failure message, which must give the reported reason.
   If a platform-only bug cannot run in CI, test the shared logic as closely as you can, and put the device steps in the PR.
   **Stop if:** the test passes before the fix.
4. **Fix the root cause.** Change the deepest cause within our control, not the symptom. When it is cheap, add the guard that let the bug happen: a type, a boundary check, a lint rule, an architecture test or an alert. Larger prevention work gets its own issue.
   Run the test until it is GREEN, then run the whole area suite.
5. **Check the blast radius.**
   - **Same pattern elsewhere:** `grep` for it. Fix it here only when it shares the root cause. Otherwise `file-bug`.
   - **Other platform:** a fix on one side usually calls for a look at the other.
   - **Stored data:** fixing code does not repair rows already wrong. Either write the repair (a migration, or a one-off script that gets reviewed) or file a follow-up. The PR says which.
   - **Old installed versions:** can the fix reach them as a server change or patch, or does it require a store release? See `release`.
6. **Verify.** Use `build` in bug mode for the full check. The minimum: the test red before and green after with both outputs pasted, area suites green, and device steps for platform bugs.
   **Stop if:** the red output or the green output is missing.
7. **Commit and open the PR.** Run `commit-check` with a `fix(<scope>): ...` message, then `open-pr`. In the PR's safety notes, explain the failure mode, who was affected and how the test shows it cannot come back unnoticed. Continue with `ci-green`, `deploy-check` and `merge-gates`.
   If the bug exposes a gap in a skill or a convention, run `lesson` (kit).

## Done when
- [ ] The regression test failed before and passes after, with both outputs kept.
- [ ] The fix hits the root cause rather than the symptom.
- [ ] The blast radius is checked and each result is in the PR.
- [ ] A non-trivial fix carries a posted plan review.
- [ ] The PR is open and describes the failure mode.

## Never
- Fix anything without a test that failed first. Pure config or infrastructure fixes show before and after evidence instead.
- Weaken or delete an existing test to get green. If that test was wrong, explain why in the PR.
- Swallow the error that exposed the bug.
- Cut a release. That is the owner's call.

## Next
- **Comes from:** `debug`, `file-bug`, `incident` (ship)
- **Leads to:** `commit-check`, then `open-pr` (ship). Later `release`, when users need a build.
