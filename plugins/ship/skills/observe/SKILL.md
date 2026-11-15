---
name: observe
description: "Read production signals to answer a health question, or add the instrumentation a change needs so the team hears about a failure before any user does. Questions: set the window, pull errors, metrics, traces and logs, check against a baseline, and keep fact apart from theory. New behaviour: errors reach the tracker, metrics stay low-cardinality, traces cover hot paths, logs stay privacy-safe, each safety signal has an alert and an owner, and a test shows it fires. Use after a release, when something seems slow or broken, or when building a new failure mode. Say: 'instrument this', '/ship:observe', 'add monitoring', 'error rate', 'why is it slow', 'add an alert', 'add metrics', 'is the release healthy'."
argument-hint: "[question | add <change>]"
license: MIT
metadata:
  version: "1.0.0"
  model: sonnet
  effort: medium
---

# Observe

`$ARGUMENTS` is one of two things. Either a question ("is release 2.3.0 healthy?", "why are reminders late since 14:00?"), or `add <change>`, meaning instrument new behaviour. Work in the environment named; if none, work locally.

**Run on:** sonnet at medium. It reads signals and writes small, well-bounded instrumentation.

## Use it when
- Someone asks whether a release or a time window is healthy.
- A change brings a new failure mode that needs a signal and an alert.

**Not for:** an outage users can see (`incident`) or a bug with no known cause (`debug`).

## Before you start
Read AGENTS.md and the repo to learn:
- Which backends exist for errors, metrics, traces and logs.
- How instruments are named and registered.
- Where alert rules live (in code, ideally).
- Health endpoints, dashboards, and each signal's target.

State plainly what is not wired up yet. Until it is, "observe" means local logs plus the test suite, and the first instrument you add becomes its own issue to wire up the rest.

## Steps
1. **Learn the signals.** Tailor this list to the product. Safety signals go first. Each line reads: signal, then the failure it catches, then a starting target.
   - **Safety and trust**
     - Critical messages (a shop's "order ready", a booking reminder): rate delivered and lag. Catches silent loss. Target: all delivered or the fallback fired, p95 lag within spec.
     - Age of the oldest unsent record in the offline queue, plus its depth, sent on reconnect. Catches data stranded on a phone. Target: younger than the spec limit.
   - **Client**
     - Crash-free sessions per release and platform. Target: 99.5% or higher.
     - Share of users with a recent background sync, split by OS version and device maker. Catches background work being killed quietly.
   - **Server**
     - 5xx rate and p95/p99 latency per route. Target: 5xx under 0.5%, latency inside budget.
     - Queue lag, failed jobs, outbox age. Target: the backlog never grows.
     - Scheduled jobs: runs, duplicates the ledger blocked, delay against schedule. Catches missed or doubled effects. Target: zero missed runs, delay inside spec.
   - **Outside providers**
     - Error rate from payment, email, SMS and push providers. Alert when it climbs.
2. **If it is a question,** fix the time window and the environment. Read what answers it: the error tracker (release, platform, issues, breadcrumbs), metrics, traces, and logs filtered by trace id. Set it beside the previous release, or the same window a week ago. Give facts with links and numbers, and keep theories in their own list.
   **Stop if:** a statement has no signal behind it and no "theory" label. A problem users can see goes to `incident`. A bug goes to `debug`.
3. **If it is `add`,** assume nobody will tell us when a new failure mode hits. Cover each of these:
   - **Errors:** any unexpected exception must hit the global handler or the tracker, along with context. Caught errors on safety paths pass through one helper. No empty catch blocks.
   - **Metrics:** name them `<app>.<area>.<thing>`, such as `shop.orders.payment_result`. Tags must be low-cardinality (`platform`, `result`, `channel`). Never put user ids, emails, free text or locations in tags.
   - **Traces:** open a span around every hot-path step, every batch and every outbound call.
   - **Logs:** structured, with named placeholders. Obey the logging rule in `security-review` (check plugin): nothing personal, no tokens, no precise locations in data leaving the device or server. A pseudonymous id may appear in a log, never in a tag.
   - **Alerts:** give every safety signal a rule: threshold, window and a named owner. Prefer code where the project supports it, and cite the rule in the PR.
   - **Product analytics** ("did people use it?") are a different job: `analytics-event` (check plugin).
4. **Prove the signal fires.** Write a unit or integration test that drives the failure path and asserts the metric or error was recorded. An in-memory metric listener or a fake error transport works.
   **Stop if:** a new failure mode lacks a signal, an alert (when safety-relevant) or a test.

## Done when
- [ ] A question: each statement cites a signal with numbers or is marked as theory, and says how many events stand behind it.
- [ ] An `add`: every new failure mode has a signal, an alert (when safety-relevant) and a passing test.
- [ ] Gaps, such as an unwired backend or a missing owner, are listed.

## Never
- Change data or settings in production. Observing is read-only.
- Send personal data in telemetry. Scrub it first, with a tested scrubber in the error reporter.
- Call a safety-critical path finished while it lacks its metric and alert.
- Read a trend into a small sample.

## Next
- **Comes from:** `release` (watch windows), `build` (new failure modes)
- **Leads to:** `incident`, `debug` (ship); `perf-check` (check)
