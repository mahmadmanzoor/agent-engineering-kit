---
name: review-code
description: "Review a diff or PR in any language or framework. Starts with the shape of the change, goes through each of 15 dimensions the diff touches (safety paths, privacy, trustworthy tests, correctness, contract, data, platform, UX, performance, observability, simplicity, placement, conventions, hygiene, required verdicts), then runs a separate mandatory design pass. Each finding states severity, file:line, a failing scenario, a fix, and the earliest test rung able to catch it. Ends with a merge risk tier. Complements the built-in /code-review command. Use before any merge. Say: '/check:review-code', 'review this', 'review the PR', 'look over my changes', 'check the diff', 'can this merge'."
argument-hint: "[PR number, branch or path; blank = current branch]"
license: MIT
metadata:
  version: "1.0.0"
  model: opus
  effort: high
---

# Review code

`$ARGUMENTS` names what to review: a PR number, a branch or a path. Empty means the current branch compared with the main branch.

**Run on:** opus at high. Reviewing is judgment, and a missed bug costs a lot.

Claude Code's built-in `/code-review` hunts bugs. This skill adds a separate design and placement pass plus a merge risk tier. For a change that matters, run both.

## Use it when
- Anything is about to merge: features, fixes, docs, CI, dependency bumps.
**Not for:** deep security or privacy work (`/check:security-review`). Measuring speed (`/check:perf-check`). Reviewing a plan before code exists (`/ship:plan-review`, ship).

## Before you start
Read AGENTS.md, CLAUDE.md and CONTRIBUTING.md for: merge gates, the review format, what the project calls safety-critical, and the commit and attribution rules. Read the issue or spec the PR links, and the plan review posted on it. Then you judge against the intent. Read the rules for each area the diff touches: `/ship:code-placement` (ship), `/server:server-rules`, `/mobile:app-rules`, `/web:web-rules`, or the project's own docs.

Fetch the diff. Adapt these to the project:
```bash
git diff origin/main...HEAD
gh pr diff <number>
gh pr view <number> --json title,body,files,labels
```
For a PR, delegate to `crew:code-reviewer` with a fresh context. The review is then independent of whoever wrote the code.

## Steps
1. **Shape.** Ask three questions. Is this one logical change? (A behaviour change mixed with a refactor: ask for a split.) Does it do what its issue asks, with nothing added? Is it reviewable? (Over about 400 hand-written changed lines: suggest a split.)
2. **Dimensions.** Check each one the diff can touch. Dimensions 1 to 3 outrank the rest.

   **Highest priority**
   1. *Safety-critical paths.* Could an effect be lost, delayed, duplicated, or sent to the wrong person? Each catch must log and surface the error. Retries have a bound and a fallback. Timers use the injected clock. Idempotency keys exist. Failure-path tests exist. So do their pair: tests proving that dedupe never swallows a real event.
   2. *Privacy and isolation.* Each resource checks ownership or membership and answers with the project's status codes. Queries filter by tenant. The logging rule in `/check:security-review` holds. Sharing is opt-in and visible. If anything here hits, run `/check:security-review`.
   3. *Tests you can trust.* They obey `/check:test-rules`: exact hard-coded expectations, no mocking of own code, behaviour rather than implementation, and the ability to fail. A new behaviour without a test written red first is a finding.

   **Behaviour**
   4. *Correctness.* UTC versus local zones, null and empty, a missing first item, events out of order, resuming after hours offline, push and pull racing, pagination edges.
   5. *Contract.* The contract file moves with the API. Generated clients are regenerated, never hand-edited. Breaking changes are versioned. Error codes stay stable.
   6. *Data.* Migrations are safe on large tables: no rewrite, nullable or defaulted columns, online indexes. Order is expand, migrate, contract. Constraints match domain limits (`/server:add-migration`).
   7. *Platform and battery.* Background work is justified and measured. OS process killers are handled. Permissions are requested after an explanation. Both platforms behave alike (`/mobile:background-work`).
   8. *Design and UX.* Use design tokens, not literal colours or strings. Strings are localised. Every designed state exists (empty, loading, error, offline). Accessibility labels and reduced motion are handled. For UI-heavy work, run `/check:a11y-audit`.
   9. *Performance.* Hunt for N+1 (a query, cache or HTTP call inside a loop), unbounded queries or ones filtered in memory, missing indexes, I/O inside a held lock, rebuild storms, UI-thread work and oversized payloads. A hot-path change with no measurement is `major` (`/check:perf-check`).
   10. *Observability.* A new failure mode raises an event or metric that someone sees. Logs carry context and no personal data. Analytics events come from the catalogue (`/check:analytics-event`).

   **Structure and process**
   11. *Simplicity.* Less code wins. One owner per rule, so nothing has a second place to update. No dead code. Names say what things are. The review checklist in `/ship:code-placement` applies here.
   12. *Layer placement.* Test each new domain type with the concept test. A parser, encoding, crypto helper or file-format code in the domain is `major`. Hand-rolling shape validation inside a handler is `minor`.
   13. *Conventions.* Apply the checklist of every rules skill whose area the diff touches. Logic, queries or transactions placed in an edge layer are `major`. Every other lapse is `minor`. An old violation in code the diff touches is a finding as well, and gets an issue. "It was already like that" is not an excuse.
   14. *Repo hygiene.* Commit style as the project defines it. No forbidden attribution. No secrets. Generated files in sync. Docs updated with the behaviour.
   15. *Required verdicts.* If the diff changes API, data, platform code, config or scheduling, a `/ship:deploy-check` verdict must be on the PR. If it touches personal data, auth, sharing or uploads, so must a `/check:security-review`. A missing verdict is `major`. A critical finding, or an unsafe row, still open and not accepted by the owner in a quoted reply is `critical`.

3. **Design pass.** Do it as its own read of the diff. It is mandatory, and speed never excuses skipping it. Ignore bugs here. Ask whether the code sits in the right place and is safe to copy. Agents copy whatever code sits next door, so one wrong placement turns into the next feature's template. Report all six checks and say what you searched for in each.
   1. **Placement.** Each new or moved file sits in its row of `/ship:code-placement` and the project's table. Check these kinds of thing: a platform decision, shared code, a loop, a rate limit, an upload body, a file format, storage, a secret, an adapter, a port, a business rule.
   2. **Duplication across features.** Is the diff building something another feature has, or will want? Typical cases: a notes-only storage class, an upload reader written twice, a rule copied into a second place, a bookings-only twin of a generic port. Run `grep`. Do not guess.
   3. **Reuse.** Generic pieces already exist: storage port, upload reader, enum mapping, access-check unit, shared module. Does the diff call them, or rebuild them?
   4. **No technical code in business layers.** Keep file formats, encodings, parsing, crypto, vendor types and protocol details out of the domain, the use-case rules and the shared core.
   5. **Homes for validation, secrets, storage.** Shape checks live in the validation unit. Each secret has its own validated config entry. Files go only through the storage port.
   6. **Plan review.** Any feature or non-trivial fix needs a plan review on its issue, posted ahead of the first code commit. The diff should follow it, or say why it departs. No review: `major`.

   A design finding is `major` when the next feature would copy it, else `minor`. A design `major` blocks the merge as any other `major` does.
   **Stop if:** the report skips any of the six checks.
4. **Write up each finding.**
   - **Severity.** `critical`: a safety-path effect can fail silently, personal data leaks, data is lost, or a core path crashes. `major`: wrong behaviour, untested new behaviour, contract drift, or a design the next feature would copy. Then `minor` and `nit`.
   - **Where:** `file:line`.
   - **Scenario:** a concrete input and the wrong outcome it causes.
   - **Fix:** a concrete change.
   - **Rung:** the rung that catches it today, and the earliest rung that should, using the ladder in `/check:test-rules`, step 8.
   A structural worry you cannot prove goes into a separate Suspicions list. It never blocks.
5. **Assign a risk tier**, independent of the verdict. **Low:** isolated, tested, easy to revert. **Medium:** shared code, migrations, platform code, or any doubt. **High:** a safety-critical path, a privacy boundary, a migration on large tables, a release-only fix.
6. **Compose the review.**
   ```markdown
   ## Code review - <short head SHA>
   Verdict: approve, approve with fixes, or changes required
   Risk tier: low | medium | high, and the reason

   ### Findings (critical, major, minor, nit)
   - [severity] file:line - the problem
     Scenario: ...  Fix: ...  Rung: today a test, should be a type.

   ### Design pass
   - [major|minor] file:line - the failed check
     Who would copy it: ...  Fix: ...
   (no findings: write "No design findings", then the six checks and what you searched)

   ### Suspicions (do not block)
   ### Clean dimensions
   List every dimension that was checked and had no finding. That is the evidence behind "no issues".
   ```
7. **Publish.** On someone else's PR, ask the user first. On the project's own PRs, posting belongs to the review. Draft a single comment in a file. Scan it for attribution the project forbids, for example with `grep -niE 'co-authored-by|generated with'`. Then post it:
   ```bash
   gh pr comment <number> --body-file <review-file>
   ```
   After the author fixes things, review only the new commits against the open findings. Post `## Code review - <new SHA> (re-review)` listing what is fixed and what remains. Ready to merge means all three hold: the newest review covers the head commit (or only a reviewed fix follows it), no `critical` or `major` finding is open, and no design `major` is open.

## Dependency-update PRs
The same gate applies, with lighter dimensions. Read the release notes across the version gap, looking for breaking changes. Scan the lock-file diff for surprise transitive bumps and install scripts. Make sure CI covered the changed area. If it did not, run those jobs yourself. Run `/ship:deploy-check` for major version jumps and native dependencies.

## Done when
- [ ] Each dimension appears as a finding or under checked and fine.
- [ ] The design pass reports six checks and what was searched.
- [ ] Each finding has severity, `file:line`, scenario, fix and rung.
- [ ] A verdict and a risk tier are stated.
- [ ] The review is posted, or the user said not to.

## Never
- Judge the author. A finding needs a scenario, not a taste.
- Approve a safety-critical change that lacks failure-path tests.
- Write "no issues" before every applicable dimension has been checked.
- Count the author's own review of their work as the independent one.
- Cut or shorten the design pass, even for a "quick review". Trim test reruns and review rounds instead.
- Post on someone else's PR without the user's OK.

## Next
- **Comes from:** `/ship:build`, `/ship:fix-bug`, `/ship:open-pr` (ship), `crew:code-reviewer` (crew)
- **Leads to:** `/check:security-review` when dimension 2 hits. `/ship:merge-gates` (ship) checks the review covers the head commit.
