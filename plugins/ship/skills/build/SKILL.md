---
name: build
description: "The build-and-prove routine for any approved change, whether feature, bug fix or maintenance. Confirms the issue and the posted plan review, searches for existing code, builds test-first with the area skills and their companion files, refactors in safe steps, gathers real command output per change type, and treats a missing device or credential as blocked, not passed. Then commit check, PR, independent review, CI, deploy check and merge. Say: '/ship:build', 'implement this', 'build the approved change', 'make it and prove it', 'refactor this', 'bump this dependency'."
argument-hint: "[issue number | spec slice | investigation report | scoped request]"
license: MIT
metadata:
  version: "1.0.0"
  model: opus
  effort: medium
---

# Build

Build the change in `$ARGUMENTS`, whether it is an issue, a spec slice, an investigation report or a scoped request, and show that it works. With no change given, ask what to build.

**Run on:** opus at medium. It writes the code and weighs the evidence.

## Use it when
- A change is approved, has an issue and has a branch. `/ship:start-issue`, `/ship:feature` and `/ship:fix-bug` all end here.

**Not for:** a loose idea (`/ship:feature-research`) or hunting a bug's cause (`/ship:debug`).

## Before you start
- Read `AGENTS.md` for build, lint and test commands per area, the checks CI skips, and the definition of done.
- Read the rules for every area you will touch before writing code: `/ship:code-placement`, `/server:server-rules`, `/mobile:app-rules`, `/web:web-rules`, `/mobile:shared-core`, and the project's own conventions doc.

## Steps
1. **Check the handoff.** Three things must exist before any code: an issue (docs and chores included), its milestone, and a branch linked to it. If one is missing, stop. File the issue with `/ship:file-issue`, `/ship:file-bug` or `/ship:spec-to-issues`, then run `/ship:start-issue`. Filing after coding is not allowed.
   Name the mode, because it sets the extra duties:
   - `feature`. Input: an issue with acceptance criteria. Duties: one test per criterion, every designed state built, nothing from "Out of scope".
   - `bug`. Input: an investigation with a root cause and a failing test. Duties: the reproduction fails before your fix and passes after it, you check what else the cause touches, and you name the data repair if stored data is already wrong.
   - `maintenance`. Input: a dependency bump, refactor, tooling or docs. Duties: behaviour stays identical, existing tests pass untouched, you invent no criteria, and architecture baselines stay empty.

   Carry over whatever the caller already did (branch, plan, failing test, approvals). Do not re-diagnose a diagnosis that holds up, and do not redesign an approved spec.
   Search first. For every component, query, helper, validator, error code or adapter you plan to add, look for an existing one and extend that instead. A second copy gets flagged in review. When no source states a business rule, ask the user.
   **Stop if:** a feature slice or non-trivial fix has no posted plan review (`/ship:plan-review`). A bug's reproduction test is the one thing that may precede it. If a product decision is still open, ask, and work on the parts that do not depend on it.
2. **Build test-first.** Work on the issue branch, not `main`. Any behaviour change follows `/check:test-first` and `/check:test-rules`. Test commands come from `/check:write-tests` and `AGENTS.md`. Pick the skill that matches each part of the change:
   - **Server:** `/server:add-endpoint` (endpoint, contract), `/server:add-migration` (schema), `/server:add-job` (scheduled or background work, outbound notifications), `/server:add-upload` (file uploads, together with `/check:security-review`)
   - **Mobile:** `/mobile:design-to-screen`, `/mobile:shared-core` (rules for both platforms), `/mobile:background-work`, `/mobile:offline-queue`, `/mobile:home-widget` (widget, live activity, tile)
   - **Web:** `/web:build-screen` (app screens), `/web:add-page` (content pages)
   - **Cross-cutting:** `/check:security-review` (personal data, auth, sharing), `/check:analytics-event` (product events)

   List the companion files before you edit. Edit the source, never generated output:
   - contract file, then the generated clients
   - bridge definitions, then the generated platform code
   - string resources, then the accessors
   - entities, then a migration
   - new settings, then the example config
   - docs that describe the behaviour you changed

   Stay inside the issue. A different defect goes to `/ship:file-bug`, not into this diff. Code that breaks a convention gets filed or fixed in its own PR. Never copy it.
   **Refactoring (maintenance mode):**
   1. Lock in current behaviour. Where tests are missing, write characterisation tests that pass on the old code, and commit them by themselves.
   2. Move code and change code in separate commits. Tests are green after each.
   3. Take small steps and stay green. Revert a red step. Do not debug forward.
   4. Leave the contract alone unless the slice says otherwise.
   5. Keep baselines empty. When a new rule arrives, fix the code in the same change. Only if that is impossible, allow a baseline that can only shrink, with a written reason per entry and an issue to clear it.
3. **Verify.** Collect proof that fits what you changed. Write each check as the command, then what it printed. A missing device, emulator, credential or SDK leaves the check blocked, and a blocked check is not a pass: state what remains.
   - Server logic: unit tests plus integration tests entering through the real entry point. Compile with warnings as errors.
   - API or auth: integration tests for callers who may and may not act. The regenerated client compiles and the contract drift test passes.
   - Migration: apply it to a local database, read the SQL it generates (`/server:add-migration`), run the data checks (`/server:db-check`).
   - UI: one test for each state, plus screenshots of each changed state on synthetic data, set beside the design.
   - Platform, background work, widgets: every platform builds, the `/mobile:device-test` rows are run on real devices, and a battery reading is taken if background behaviour changed.
   - Safety-critical paths (the project keeps a list): a test per failure mode from `/check:test-rules` shows that the action still happens or the failure is shown to the user.
   - Privacy: the `/check:security-review` checks, plus tests for forbidden callers and removed members.
   - Speed-sensitive code: `/check:perf-check` against the budget.
   - Maintenance: full test suites and lint in every affected area. A native dependency bump also needs every platform build.

   **Stop if:** an acceptance criterion has no evidence.
4. **Review and hand off.**
   1. Run `/ship:commit-check`, then commit in small conventional commits.
   2. Run `/ship:open-pr`. It starts `crew:code-reviewer` on fresh context to post a review on the PR. Authors never review their own work. Add `/check:security-review` for personal data, auth, sharing or uploads.
   3. Continue with `/ship:ci-green`, `/ship:deploy-check` and `/ship:merge-gates`.

   Write a closing report. It also seeds the PR body. Cover: what was built against the criteria; files changed, by area; decisions made; checks run with real output; limits and unverified items; debt added or found, each with an issue.
   Report implemented, verified, PR open, CI green, merged and released as separate states. Never promote one to the next.

## Done when
- [ ] Every acceptance criterion has evidence: a command and its output.
- [ ] Required checks pass, or the blocked ones are named.
- [ ] The plan review's decisions were followed, or the PR lists the deviations.
- [ ] The report lists implemented, verified, PR open, CI green, merged and released separately.

## Never
- Write code that no red test asked for. Config, docs and generated code use their own checks.
- Weaken or delete a test so the change passes.
- Swallow an error on a safety-critical path.
- Claim "tests pass" without running them.

## Next
- **Comes from:** `start-issue`, `feature`, `fix-bug` (ship)
- **Leads to:** `commit-check`, `open-pr`, `ci-green`, `deploy-check`, `merge-gates` (ship); `review-code` (check)
