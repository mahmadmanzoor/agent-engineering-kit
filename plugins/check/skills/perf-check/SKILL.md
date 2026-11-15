---
name: perf-check
description: "Decide whether something is fast enough, and make it so. Budget first, then a release-mode baseline on the reference device, a profiler to find the cause, one change at a time, a guard, and a before-and-after report. Handles launch time, dropped frames, memory, download size, battery, web vitals, endpoint latency, slow SQL and N+1. Use for any change on a hot path, or anything that feels sluggish. Say: '/check:perf-check', 'is this fast enough', 'performance', 'slow endpoint', 'dropped frames', 'battery drain', 'app size', 'load test', 'N+1'."
argument-hint: "[target: screen, page, endpoint, query, job or PR]"
license: MIT
metadata:
  version: "1.0.0"
  model: sonnet
  effort: medium
---

# Perf check

`$ARGUMENTS` is the thing to measure: a screen, page, endpoint, query, background task or PR. Compare it with the budgets and fix what is over. No argument: use the hot paths in the branch diff.

**Run on:** sonnet at medium. Fixed loop; each step ends in a number.

## Use it when
- A change touches a hot path, or something feels slow.
**Not for:** habits while coding (no call inside a loop, bounded lists, UI thread kept free). Those sit in `/ship:code-placement` (ship), `/server:server-rules`, `/mobile:app-rules` and `/web:web-rules`. This skill measures and fixes.

## Before you start
- Find the budgets file (like `docs/performance-budgets.md`) and the devices or environments it names as reference.
- Check which guards already exist: query-count asserts, load scripts, size checks, benchmarks.
- Open the matching reference: [backend](references/backend.md), [web](references/web.md), [mobile](references/mobile.md).
- No budgets file? Draft one and get the user's OK before using it. Suggested lines: launch time, frame time, memory, size, battery, API p95 per class of route, query time with 10x the data you hold today.

## Steps
1. **Budget.** Take the one that fits the question. None fits: propose one in the budgets file first.
2. **Baseline.** Use the reference device or environment, in release or profile mode. Run it 3 times or more and take the median. Debug builds, simulators and localhost on a laptop prove nothing for app or web speed.
   **Stop if:** there is no before number. Do not optimise.
3. **Cause.** Profiler, query plan or trace. No hunches.
4. **One change.** Remeasure the same way.
5. **Guard.** Query-count test, plan test, load threshold, size limit or CI benchmark, where one fits.
6. **Report.** Before, after, device or environment, mode, run count, the change.
   **Stop if:** there is no after number. Do not say "faster".

## What to inspect

| Symptom | Method |
|---|---|
| Slow start | Trace to first frame or first useful paint. Suspects: work before that frame, eager setup, big asset decoding. |
| Jank (scroll, map, animation) | Frame timeline in profile mode, plus re-render tracking. Shrink what re-renders, cache heavy children, do parsing and geometry work away from the UI thread, limit how many items render (cluster, or virtualise the list). |
| Frame data you can repeat | Drive the screen from an integration test. Log p90 and p99 frame times and the share of janky frames. |
| Memory creep | Snapshot after 10 minutes of use. Suspects: caches that only grow, subscriptions never released, retained images. |
| Big app | Platform size analysis on the release build. Drop unused assets and fonts, compress images, split by architecture, check what new dependencies add natively. |
| Animations | Must stop off screen and under reduced motion. None may run in the background. |
| Battery | A budget like any other. Count work per hour: wake-ups, network calls, sensor time. Compare an active run with an idle one. Real devices, platform battery tools, a low-end device in the set. |
| API under load | Load script, ramping users, think time. Budget-based thresholds (p95, error rate). Local or dedicated test environment only; staging needs the user's OK. |
| Hot function | Micro-benchmark, before and after. |
| Slow query | Plan with real execution stats over 10x synthetic data. Suspects: full scans of big tables, missing indexes, no time filter on time-partitioned tables, ORM N+1. |
| Costly or frequent statements | Database statement statistics. App-side slow-query log threshold, parameter values never logged. |
| Query count per call | API test: reset a counter, call, assert the exact count with one item and with several. An N+1 then fails. |
| Fan-out, realtime | Trace event to delivery. Group sizes, backplane load. |

## Done when
- [ ] Before and after numbers exist, with device or environment, mode and run count.
- [ ] A tool found the cause. One change per measurement.
- [ ] A guard exists, or the reason for none is written down.
- [ ] Safety tests pass.

## Never
- Optimise without a before number, or write "should be faster".
- Change two things between measurements.
- Load-test production, or use real users' data in performance fixtures.
- Buy speed with safety. Fewer background runs must not delay a critical notification. The safety tests decide.

## Next
- **Comes from:** `/check:review-code` (dimension 9), `/ship:build` (ship), `/mobile:background-work` (mobile)
- **Leads to:** `/ship:observe` (ship) for production signals. `/server:db-check` (server) for read-only query plans. `/mobile:device-test` (mobile) for battery rows.
