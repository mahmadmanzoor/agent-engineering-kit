---
name: file-bug
description: "Turn a bug report into an issue using one fixed template: a title that names the symptom, actual and intended behaviour with the spec or design cited, reproduction steps from a clean state, environment, frequency, priority (P0 for any silent failure on a safety-critical path, or exposed or lost data), safety impact, evidence free of personal data, a cause labelled as theory, and the regression test to add. Nothing is created before the owner approves. The issue joins its epic. Say: '/ship:file-bug', 'file a bug', 'log this bug', 'open a bug issue', 'write this up as a bug'."
argument-hint: "[what happened | error link | user report | --parent <epic> plus a description]"
license: MIT
metadata:
  version: "1.0.0"
  model: sonnet
  effort: low
---

# File bug

File `$ARGUMENTS` as a tracked issue. The input may be free text, a link to an error tracker, a user's report, or `--parent <epic>` followed by text. Reuse the results of any investigation from this conversation rather than redoing it. If nothing was given, ask: what happened, in which place, and what was expected?

**Run on:** sonnet at low. It records the bug and does not diagnose it.

## Use it when
- Behaviour contradicts the spec and no issue exists yet.

**Not for:** finding the cause (`/ship:debug`) or fixing it (`/ship:fix-bug`).

## Before you start
From `AGENTS.md` take: the tracker, labels, milestones, what each priority means, how versions and environments are named, and which paths are safety-critical.

## Steps
1. **Collect the fields.** Ask for what is missing, and never guess.
   - **Title.** Use `fix(<area>): <what the user sees go wrong>`, up to 70 characters. Example: `fix(notes): edits made offline vanish after reconnect`.
   - **Actual result.** Say what happened, with the error text copied exactly.
   - **Intended result.** Say what should happen and point to the spec or design that says so.
   - **Reproduction.** Number the steps, beginning from a clean state. If you cannot reproduce it yet, say "not yet reproducible" and list your attempts.
   - **Environment.** App version, platform and OS, device or browser, and the server commit or environment.
   - **Frequency.** Every time, x out of y tries, or a single occurrence.
   - **Priority.**
     - P0: a safety-critical path may fail without a sound, personal data reaches someone it should not, or data is lost.
     - P1: a core flow is broken and users cannot work around it.
     - P2: a workaround exists, or the flow is not core.
     - P3: looks wrong, works fine.
   - **Safety impact.** Ask two questions. Could a critical action be skipped, late or repeated? Could someone see another person's data? A yes to either adds `safety-critical` or `privacy` and sets the priority to P1 at minimum.
   - **Evidence.** A tracker link, log lines, screenshots made from synthetic data, a failing test's name.
   - **Suspected cause.** Include only what the evidence supports, and call it a theory. "Unknown" is a valid answer.
   - **Area and blockers.** Add the `area:*` label. If the fix has to wait, add `blocked`, `blocked:<reason>` and a `**Blocked by:**` line.
2. **Draft the body.**
   ```markdown
   **Priority:** P1 | **Safety impact:** none / action can be missed / data exposed / data lost | **Seen in:** <version> <platform> / <environment>
   ### Actual
   ### Intended
   ### Reproduction
   1. ...
   ### Environment
   ### Frequency
   ### Evidence
   ### Suspected cause (a theory, not fact)
   ...
   ### Regression test
   Name the test to add: it must fail today and pass once the bug is fixed (`<path>`, `<name>`).
   ```
   Scrub it before you show it. Replace real people with "User A" and "User B", and remove from text, logs and screenshots any name, email, phone number, address, coordinate, account id, token or session id.
3. **Get approval.** Show the title, labels and body.
   **Stop if:** the owner has not approved.
4. **Create it and link it.**
   ```bash
   gh issue create \
     --title "fix(notes): edits made offline vanish after reconnect" \
     --body-file bug.md \
     --label "type:bug,P1,area:sync" \
     --milestone "M2 offline notes"
   ```
   Use the milestone of the feature the bug breaks.
   Append `safety-critical` to the labels when it applies. When the feature has an epic, attach the issue (see `/ship:file-issue` for the commands). A bug found in a merged PR may get a comment with the link, but only if the owner agrees.
5. **Report back** with the link, the priority and the next step. Cause unknown, or only suspected: `/ship:debug`. Cause proven by an investigation: `/ship:fix-bug`.

## Done when
- [ ] The issue matches the template and names a regression test.
- [ ] The priority agrees with the safety impact.
- [ ] No personal data appears in text, logs or images.
- [ ] The owner said yes before anything was created.

## Never
- Bury a P0 or `safety-critical` bug. It opens your reply.
- Paste personal data or attach a screenshot taken from a real user.
- Present a theory as fact. Saying "not our bug" takes evidence.
- Bundle bugs. File one per issue. The one exception: two symptoms from one proven cause share an issue that lists both.

## Next
- **Comes from:** a report, `debug`, `incident` (ship), a review finding
- **Leads to:** `debug` or `fix-bug` (ship)
