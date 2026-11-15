---
name: incident
description: "Run a live production problem from first alert to handoff. Sets a severity: SEV1 if  leaks, SEV2 if a core flow is down, SEV3 if it is only degraded, stops the harm before hunting the cause, keeps a timeline, drafts user messages for approval, investigates read-only, fixes through the normal bug path, proves recovery with the signal that raised the alarm, then queues a postmortem. Use when real users are affected right now. Say: 'outage', 'payments failing', '/ship:incident', 'everything is broken', 'prod is down', 'emergency', 'notifications not arriving', 'users can see other users data'."
argument-hint: "[what is happening]"
license: MIT
metadata:
  version: "1.0.0"
  model: opus
  effort: high
---

# Incident

Handle the live problem in `$ARGUMENTS`. Be quick, but get the user's explicit OK before you touch production in any way.

**Run on:** opus at high. Under pressure one wrong move can deepen the damage.

## Use it when
- Customers are being hit now by something broken, leaking or lost.

**Not for:** a bug that is not live (`debug`) or a routine post-rollout look (`observe`).

## Before you start
Read AGENTS.md and `docs/runbooks/`. Find these five facts:
- How to halt a rollout.
- How to roll back each release path.
- How to flip a feature flag.
- Where to post a status update, or how to send an in-app notice.
- Which dashboards carry the safety signals.

A missing runbook goes on the postmortem follow-up list. Do not invent a destructive step to cover for it.

## Steps
1. **Rate it in the first minutes.** If two levels fit, take the higher. The safety-critical list in AGENTS.md defines "safety".
   | Level | Meaning | Shop and notes examples |
   |---|---|---|
   | SEV1 | Someone may be unsafe, or data is out in the open | Order-ready alerts never arrive. A customer sees another customer's address. Orders vanish. Every launch crashes. |
   | SEV2 | A core flow is down, safety intact | Nobody can sign in. Checkout fails for many shoppers. Notes stop syncing for many. |
   | SEV2, data integrity | Records are duplicated, corrupted or lost. Becomes SEV1 if it touches safety or money, or exposes data at scale. | One booking saved twice. Reminder emails sent twice. Edits lost after a sync. |
   | SEV3 | Slower or partly broken, with a workaround | One screen broken. One phone brand affected. Reports run slowly. |

   Priority follows level: SEV1 is P0, SEV2 is P0 or P1, SEV3 is P2.
2. **Open one tracking issue.** Use `file-bug`. An incident counts as the user's go-ahead to record it. Title it `incident: <symptom>`, give it the level's priority, and add `safety-critical` or `privacy` labels where they apply. Every later artifact (timeline, fix, postmortem) links to it.
3. **Stop the harm before finding the cause.** Per move: propose, get the OK, act, then check. Start with the quickest.
   1. Pause the staged store rollout.
   2. Go back to the last good build, for an app patch or a backend deploy (`release`).
   3. Turn off the flag that guards the broken behaviour.
   4. Privacy leak: shut the leaking endpoint or method (answer not-found), even if that breaks a feature.
   5. Critical delivery failing: test the fallback channel. A dead fallback is the first thing to repair.
   6. Duplicate or runaway scheduled work (double emails, repeat charges): pause the scheduler or disable that one job, empty or stop the worker queue, and investigate only after that. Look for a second scheduler instance left running by a deploy.
   **Stop if:** the signal that showed the problem has not returned to normal and the user has not chosen to live with it while the fix is built.
4. **Log a timeline from minute one** in `docs/postmortems/<YYYY-MM-DD>-<slug>.md`, or wherever the project keeps it. One line per event: UTC time, what was seen, what was done, by whom. No opinions.
5. **Draft the user message.** If safety or data is involved, write a status or in-app note for affected users. Example: "Reminders may arrive late. Please contact guests directly if it is urgent." Schedule an update every 30 to 60 minutes until it is over. Say what you know and when the next update comes. Leave out guesses.
   **Stop if:** anything is about to be sent or posted without the user's OK.
6. **Find the cause.** Run `observe` over the incident window, then `debug`. Use read-only queries only (`db-check`, server plugin). List facts and hypotheses apart.
7. **Fix, then prove recovery.** Route the fix through `fix-bug` (regression test, `open-pr`, `ci-green`, `merge-gates`) and ship it by the right `release` path. Show recovery with the very signal that raised the alarm, for example delivery back at 100% or the crash-free rate above target. A finished deploy proves nothing. List any damage to stored data (wrong records, lost history, wrong messages sent) and plan its repair as its own piece of work.
8. **Close out.** Record the severity, start and end times, impact (users affected, what they saw), mitigation, root cause (or "unknown yet") and follow-up issues. Then run `postmortem`. SEV1, SEV2 and every data-integrity incident must have one. For SEV3 it is advised.

## Done when
- [ ] A level is set and the tracking issue is open.
- [ ] The original signal shows the harm has stopped.
- [ ] The timeline is complete and factual.
- [ ] The original signal also confirms recovery.
- [ ] The closing summary is written, and `postmortem` is queued where required.

## Never
- Hunt for the cause before the harm is contained.
- Erase data, rewrite history or edit live records without a specific, explicit OK.
- Send users a message, or post in public, before the user says yes.
- Put guesses in a status update.

## Next
- **Comes from:** an alert, a user report, `observe`
- **Leads to:** `debug`, `fix-bug`, `release` (rollback), `postmortem` (ship)
