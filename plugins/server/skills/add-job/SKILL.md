---
name: add-job
description: "Add or change scheduled and background work, and the notifications it sends. Confirm a stored time is not enough, then design one scheduler, idempotent jobs, claimed rows, a sent-ledger, access checks at run time, zone-aware schedules and a single retry owner, with failure-path tests written first. Use for reminders, digests, expiries, retries and cleanup. Say: '/server:add-job', 'cron job', 'background job', 'scheduled task', 'worker', 'send a reminder', 'send an email when', 'notification sent twice'."
argument-hint: "[what must happen, and at what time]"
license: MIT
metadata:
  version: "1.0.0"
  model: opus
  effort: high
---

# Add a job

Build or change the job for `$ARGUMENTS`. No argument? Ask: what happens, when or after which event, to whom, and what is the harm if it fires twice or not at all?

**Run on:** opus at high. Jobs fail quietly. They never run, or they run twice, and then someone is charged twice or gets no reminder.

## Use it when
- Something has to happen at a set time: send, charge, escalate, expire with side effects, clean up.
- A notification went out twice, or never.

**Not for:** state that only changes with time. Store a timestamp and compare it with now. That needs no job.

## Before you start
Read `AGENTS.md`, the conventions and the decision records. Look for a runner, scheduler, outbox or notification port that already exists, and reuse it. Read the job tooling and delivery rules for the stack in [references/stacks.md](references/stacks.md) and in the stack files of `server:server-rules`. Learn how the app deploys (rolling, blue and green, several replicas), because that decides how you guarantee one scheduler.

A job that sends something people depend on is safety-critical when the project's list in `AGENTS.md` says so.

**Stop if:** you cannot say which runner and scheduler exist, where jobs live, and what a deploy does to a job already running.

## Steps
1. **Confirm a job is needed.** "Paused until 17:30" is a stored time that reads compare with now. Use a job only when an action must fire at a time.
2. **Design it.** Decide each point below.

   - **Scheduler:** exactly one instance per environment, and the guarantee must hold (a lock, one replica, platform cron). That includes deploys, when old and new versions overlap. Workers can be many.
   - **Job body:** thin. Load ids, call one use-case method. Business rules stay in the domain.
   - **Finding work:** query due rows in bounded batches. Claim each row with a skip-locked row lock or a lease column with an expiry, so two workers never take the same one.
   - **Once-only effect:** delivery happens at least once, so make the effect happen once. Before sending, insert a ledger row with a unique key (item id plus due time). A unique violation means skip. The ledger also stores the outcome.
   - **Access:** check membership, consent and preferences again when the job runs.
   - **Time:** store the person's zone id and local time. Compute the instant in the domain. Decide how DST gaps and overlaps behave, and test them.
   - **Retries:** the job is the single retry owner. Use bounded attempts, backoff with jitter, then a visible failure (a dead-letter row, an alert or a fallback channel). The send client never retries on its own.
   - **Enqueue:** after the transaction commits, or via an outbox row written in the same transaction. Never earlier.
   - **Deploys:** workers drain by finishing or releasing their claim. A lease expiry hands abandoned rows back. Schema changes stay compatible with jobs already queued.
   - **Metrics:** job lag, failures by kind, how often "already sent" fires, backlog size. Each safety signal gets an alert with an owner (`ship:observe`).

   Outbound notifications (email, SMS, push, webhooks) add these rules:
   - One notification port, one adapter per provider. Features never call a vendor SDK.
   - All templates sit in one place, keyed by kind and language. Jobs never assemble message text.
   - Check preferences and unsubscribe status at send time. Keep transactional and marketing kinds apart. Every non-essential message offers a way to unsubscribe.
   - Logs, metrics and the ledger hold ids only, no other personal data (`check:security-review`).
   - Provider calls get a timeout and a circuit breaker. Retries belong to the job. Add a fallback channel when the spec asks for one.

   **Stop if:** the design has no scheduler guarantee, claim mechanism, ledger key, retry owner or run-time re-check. Send it through `ship:plan-review`.
3. **Write tests first, failure paths first.** Fake the clock and the notification port, with the port recording what it was asked to send (`check:test-rules`). Cover:
   - the job runs twice for one due item and yields one notification and one ledger row; pair it with a test that a truly new due item still sends;
   - two workers claim at the same moment and every item is handled once (synchronise with a gate, not a sleep);
   - the member left, unsubscribed, or the item was cancelled before run time: nothing is sent and the ledger says why;
   - the provider fails: the exact backoff sequence runs, then a visible failure;
   - the process dies after sending but before recording: the next run does not resend, or the design states and tests the accepted risk;
   - the due instant itself: not one tick early, not never;
   - DST spring-forward and fall-back for local-time schedules, and a far-away zone;
   - a rolled-back change enqueues nothing.

   **Stop if:** any test is red for the wrong reason.
4. **Build and verify.** Build per `server:server-rules`. Add the ledger and lease columns, plus the unique index, through `server:add-migration`. Run it locally on the real database and the real runner with one scheduler and two workers. Then run the area suite. In the PR, explain how one scheduler is kept during deploys, and list each failure mode with its test. `ship:deploy-check` handles the deploy overlap.

## Done when
- [ ] Every step 3 test passes, with command and output shown.
- [ ] The design names the scheduler, claim, ledger key, retry owner and re-check.
- [ ] A local run with one scheduler and two workers sends no duplicate.
- [ ] Lag and failures have metrics and alerts.

## Never
- Never run two schedulers.
- Never ship a job that is not idempotent.
- Never send until the ledger row is in place.
- Never hide a failure. Its owner retries it, or it turns into a visible failure.
- Never let an adapter decide whether to notify. The use case decides.
- Changes to the timing or frequency of something people rely on go through `ship:write-spec` first.

## Next
- **Comes from:** `build`, `write-spec`, `plan-review` (ship); `server-rules` (server)
- **Leads to:** `add-migration`, `add-endpoint` (server); `ship:observe`; `ship:deploy-check`; `check:security-review`
