---
name: ci-green
description: "Shepherd a pull request through its pipeline and diagnose red runs. Watch the head commit's checks, trace the first error and reproduce it locally, time a slow pipeline before tuning it, and edit workflows with care (stable job names, pinned actions, secrets out of files, no self-hosted runner on a public repo). Use while a PR waits on its pipeline or after a run goes red. Say: '/ship:ci-green', 'watch the pipeline', 'red build, why?', 'checks are failing', 'get this PR green', 'CI takes too long', 'write a new workflow'."
argument-hint: "[ship <PR> | debug <run or PR> | optimize | workflow <what to change>]"
license: MIT
metadata:
  version: "1.0.0"
  model: sonnet
  effort: medium
---

# CI green

Handle `$ARGUMENTS`: `ship [PR]` (the default), `debug [run|PR]`, `optimize` or `workflow <change>`.

**Run on:** sonnet at medium. The work is reading logs, sorting failures and re-running known commands.

## Use it when
- A PR is waiting for checks.
- CI is red and you need to know why.
- CI is slow, or a workflow needs a change.

**Not for:** a failing test whose cause is outside the diff (use `debug`).

## Before you start
Open the pipeline files first (`.github/workflows/*.yml`, or the project's CI config). If a file and this skill or AGENTS.md disagree, the file is right. Report which line has gone stale. Collect from AGENTS.md:
- the checks the merge gates require (`merge-gates`)
- the areas CI skips. You run those by hand and paste the output into the PR.
- the runner type and the location of the CI docs

Read the path filters as well. A skipped job is a pass only when its area was untouched.

## Steps
1. **Ship: watch the checks.**
   ```bash
   gh pr checks <PR> --watch --interval 20
   gh pr view <PR> --json headRefOid,statusCheckRollup,mergeable,mergeStateStatus
   ```
   The checks must belong to the PR's current head commit. A new push takes a moment to produce a run. Red means step 2. Green means one more look: does the head include current main? A `BEHIND` PR, or one just retargeted, needs main merged in and pushed, then a fresh green run.
   **Stop if:** a required check is red or absent on the head commit, or the head is missing current main.
2. **Debug: find the first error.**
   ```bash
   gh run list --branch <branch> --limit 3
   gh run view <run-id> --log-failed | head -80
   ```
   Scan the log from the top. The first error is the real one, because later ones are usually fallout. Put it in a class and run CI's own command on your machine:
   - **Build or compile (warnings as errors):** the CI build command, same configuration.
   - **Test:** that test by name, then the file around it.
   - **Lint, analyze, format:** the same linter, reading the repo's config.
   - **Dependency resolution:** diff the lock files. A recent bump is the usual culprit.
   - **Environment (runner offline, service or registry down):** nothing to reproduce. The log line is your evidence.
   - **Toolchain version:** compare the pinned version with yours. Change the pin on purpose, in the same commit as the code that needs it.

   Fix the cause in code, run `commit-check`, push, and watch the new run.
   **Stop if:** your plan is to re-run so a test, lint or build failure goes away. The sole exception is a plainly environmental failure: retry once per commit and quote the log line that proves the cause. A test that fails now and then is flaky. Fix it or delete it (`test-rules`, check plugin). Do not re-run it until it passes.
3. **Optimize.** Find the slowest jobs and steps over three runs (`gh run view <id> --json jobs`). Then change a single thing and measure again. Ideas, roughly by payoff:
   - dependency caches keyed on lock files
   - path filters, so docs-only changes skip builds
   - independent jobs in parallel
   - slow integration tests in their own job
   - parallel test execution
   - `concurrency` to cancel superseded runs

   Cancel superseded runs for pull requests only. Main runs every commit to the end, so a red main always maps to one commit. Report timings before and after.
4. **Workflow changes.** Treat them like code.
   - Branch as `ci/...` or `chore/ci-...` and open a PR.
   - Job names are an interface. Merge gates and branch protection match on them. Rename a job and update the gate in one PR.
   - Pin third-party actions. A major version is the minimum. For any action that can write, use a full commit SHA. Give each workflow the smallest `permissions` it needs.
   - Secrets belong in repository or environment secrets, added with the user's OK. Not in files. Never print one.
   - A public repository never gets a self-hosted runner. Any stranger can open a fork PR and run code on that machine. If a private repository is about to go public, remove its self-hosted runners first.
   - Fork PRs receive no secrets. Never let a `pull_request_target` workflow check out the PR's code and execute it.
   - Prove it by pushing the branch and watching the run. For jobs that only run on main, start them by manual dispatch.
   - With the issue gate in use, add a check that the PR links an issue.
   - Apple-platform builds need a macOS runner. Android and most cross-platform analyze and test steps run fine on Linux.

   A starter workflow is in [references/github-actions.md](references/github-actions.md).

## Done when
- [ ] Every required check is green on the head commit, or skipped because its area did not change (links kept).
- [ ] The head contains current main.
- [ ] After a failure, the report names the first error, the root cause, the fix commit and the link to the green run.

Report each job with its state and a link.

## Never
- Let main stay red. Nothing else merges until it is fixed.
- Loosen a check to turn it green (skip a test, lower a threshold, make a job optional). That choice needs its own reviewed change.
- Force-push, or push to another person's branch, without the user's OK. Plain fix commits on the PR branch need no ask.

## Next
- **Comes from:** `open-pr`, `fix-bug` (ship)
- **Leads to:** `deploy-check`, then `merge-gates` (ship). Use `debug` when the cause is outside the diff.
