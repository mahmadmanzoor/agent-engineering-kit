---
name: debug
description: "Find why a bug happens, without fixing it. Reproduce it first as a failing test on a fix branch, describe the symptom exactly, hold at least five rival hypotheses, narrow them with history, logs and read-only data, ask why five times, measure the blast radius, and write a report that also says how to stop the whole class of bug. Use when something is broken and the cause is unknown. Say: '/ship:debug', 'why is this happening', 'find the root cause', 'dig into this bug', 'what is going wrong', 'it used to work', 'debug this'."
argument-hint: "[symptom | issue number | error link | user report]"
license: MIT
metadata:
  version: "1.0.0"
  model: opus
  effort: high
---

# Debug

Find the root cause behind `$ARGUMENTS` (a symptom, an issue, an error link or a user report). This skill diagnoses and `fix-bug` repairs. With no argument, ask four things. What happened? Where (device, OS, version, environment)? What did the user expect? How often does it occur?

**Run on:** opus at high. A wrong cause sends the fix to the wrong place.

## Use it when
- Behaviour is wrong and the reason is a mystery.
- A bug issue is open without a confirmed cause.

**Not for:** a production problem that is live right now (use `incident` first), or a bug whose cause is already known (use `fix-bug`).

## Before you start
Open AGENTS.md, CLAUDE.md and CONTRIBUTING.md and note: the local commands for tests and the app, the places logs and errors go, the safety-critical list, and the way to read data without writing (`db-check`, server plugin).

If you were handed an issue number, read that issue before anything else (`gh issue view <n>`, or the tracker's own tool). Missing fact: ask once, then offer to save it in AGENTS.md.

## Steps
1. **Judge the stakes.** By default a symptom is safety-critical when it skips or repeats a critical action, shows data to the wrong person, or loses or corrupts data. A project list replaces this default.
   Tell the owner now, ahead of the deeper work. A problem live in production goes to `incident` first.
   **Stop if:** the symptom is safety-critical and the owner has not been told.
2. **Secure an issue and a branch.** Because the reproduction test is code, it needs both.
   No bug issue? Run `file-bug` with what you have, then make a `fix/<n>-<slug>` branch through `start-issue`. The main branch stays untouched, and `fix-bug` later continues on this one.
   **Stop if:** you are on the main branch.
3. **Reproduce it.** Write the smallest failing test, or the exact steps. Pick by kind of bug:
   - Domain logic: one unit test with the same inputs, and a fake clock for anything time-based.
   - API, auth or data: an integration test through the real entry point, against a real local database.
   - UI or client state: a UI test with fake time and in-memory fakes at the boundaries.
   - Background or platform: emulator or simulator steps from `device-test` (mobile plugin), with device logs captured.
   - One device or vendor only: the `device-test` steps on that device, noting its battery and permission settings.

   Run it. The failure must match the report. A test that dies from broken setup proves nothing. If it will not reproduce yet, reproducing is now the task, so log every attempt.
   **Stop if:** the test passes, or fails for a different reason.
4. **Pin the symptom.** Write down four things: what is observed, when (always, after one action, only in the background, on one vendor), since when (`git log --since`, or the release), and what should happen instead.
5. **List hypotheses.** Write at least five before chasing any one. Usual suspects in a notes or booking app: a permission the OS downgraded, background work the OS killed, stale cache, a time zone or UTC slip, repeated or out-of-order events, a wrong membership filter, an expired token, an offline queue that never flushed, two channels racing, a retry layer that sends twice.
   Keep facts in one column and theories in another. Write the reason for each rejection, so nobody repeats it. Three rejections in a row mean your assumptions are suspect. Revisit them before trying more variants.
6. **Narrow it with evidence.**
   - Code: trace backwards from the symptom to the entry point. Use `git log -L` and `git log --oneline -20 -- <file>`. Read every catch on the path.
   - Errors and logs: the error tracker, server logs, and `observe` for the time window.
   - Data: read-only queries that compare what the code produced against what it should have produced. Aggregate or redact. Never paste personal data.
   - Device: device logs, plus battery and permission state.
7. **Reach the root cause.** Keep asking why until the answer has no deeper explanation. The fix targets the deepest cause within our control. Then ask why it was breakable, and name the earliest rung of the `test-rules` ladder (check plugin) that should have caught it.
8. **Measure the blast radius.** Check other platforms, vendors, versions and tenants. `grep` for other code with the same pattern. List stored rows that are now wrong and will need repair after the fix.
   **Stop if:** there is no failing reproduction, or the cause chain is not backed by facts. Mark the status "unverified" and name the evidence that is missing.
9. **Write the report.** Save `docs/investigations/<YYYY-MM-DD>-<slug>.md` and summarise it in your reply:
   ```markdown
   # <symptom in one line>
   Issue: <link> | Status: root cause found / not reproduced / unverified
   ## How to reproduce   (test name or exact steps, plus the failing output)
   ## Why it happens     (the chain of whys, ending at file:line)
   ## Proof              (each fact and where it came from)
   ## Dead ends          (hypothesis, and the reason it fell)
   ## Who else is hit
   ## Suggested repair   (approach only, no code) and the regression test
   ## Stop the next one  (type, lint, test, alert or placement row)
   ```

## Done when
- [ ] A reproduction fails for the reported reason, and its output is kept.
- [ ] The cause chain rests on facts, or the status reads "unverified".
- [ ] At least five hypotheses are listed with their outcomes.
- [ ] The blast radius is written down.
- [ ] The report is saved and summarised.

## Never
- Declare a root cause with confidence before a reproduction exists.
- Mix facts with theories. Tag every claim.
- Write to production or shared data, or fix the code. The one piece of code you add is the reproduction test, on the fix branch.
- Paste personal data into the report.

## Next
- **Comes from:** `file-bug`, `incident` (ship)
- **Leads to:** `fix-bug` (ship). Use `lesson` (kit) for the "prevent the class" idea.
