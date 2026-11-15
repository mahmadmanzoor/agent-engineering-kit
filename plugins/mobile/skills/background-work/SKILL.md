---
name: background-work
description: "Change mobile background work without letting it fail silently: periodic sync, queued uploads, or a long task the user can see. Rules are decided in the shared core, the app-to-native contract changes first, the OS mechanism fits the job, every stop reports a reason, failure-path tests come first, and emulator, device and battery checks close it. Use when anything runs while the app is off screen. Say: '/mobile:background-work', 'sync while closed', 'task dies when I leave', 'job stops after a while', 'battery drain', 'does not restart after reboot'."
argument-hint: "[what should run in the background]"
license: MIT
metadata:
  version: "1.0.0"
  model: opus
  effort: medium
---

# Background work

Work on the background behaviour in `$ARGUMENTS`. With no argument, ask two things: what must run while the app is closed, and what the user relies on it for.

**Run on:** opus at medium. A silent stop or a battery drain hurts users and is hard to spot.

Background work fails without a sound. The OS kills the process, a battery saver delays the job, a permission gets downgraded, and nobody finds out. Once users depend on the result (fresh data, alerts, an upload they expect), the work is safety-critical. It must never stop silently, and it needs failure-path tests plus a test on a real device.

## Use it when
- You add or change anything that runs while the app is off screen.
- Work "stops after a while", drains the battery, or does not come back after a reboot.

**Not for:** the design of the queue itself (`offline-queue`), or where rules live (`shared-core`).

## Before you start
Read `AGENTS.md`, `CLAUDE.md`, decision records and native READMEs. Also read the battery and performance budgets. Locate the bridge contract between app and native code, the shared core (`shared-core`), the queue (`offline-queue`) and the test command for each.

Open the platform notes: [references/android.md](references/android.md) and [references/ios.md](references/ios.md). A cross-platform framework app also needs [references/flutter.md](references/flutter.md). Other frameworks' background plugins raise the same questions.

Where the rules live is a recorded decision (`decision` in `kit`). Either a shared native core holds them, or the framework's own language holds them as pure, tested code with only OS glue on the native side. If no record exists, raise the question before you write any rule.

**Stop if:** you cannot yet name, per platform, the OS mechanism that runs this job today and the place its rules live.

## Steps
1. **Decide in the core.** Every new or changed rule goes into the core, with its test written first (`test-first` in `check`). Rules here means the schedule, the frequency, the retry policy, the blockers and the reporting. With no core, write the rule once per platform as a tested pure unit that shares test vectors, and raise a design question.
2. **Run the core tests on both targets.**
3. **Start from the contract.** A new field or call between app and native code starts in the bridge definition. Regenerate both sides from it. Never hand-edit generated files.
4. **Keep the native shells thin.** They do OS work only. A new OS input arrives as a parameter. A new adapter method returns failures, never "empty". A policy branch written in shell code belongs in step 1.
5. **Apply the platform rules.**

   *Pick the right OS mechanism*
   - Continuous work the user can see runs as visible foreground work. Its ongoing notice says what is running and offers actions.
   - A transfer the user started uses the OS's user-initiated transfer feature, or a background transfer session that survives suspension.
   - Deferrable work belongs in the OS job scheduler, with constraints such as network or charging.
   - Learn the time limits on current OS versions. Some foreground types are capped per day. Design for being stopped.
   - Never build a timer loop that holds the process awake.

   *Run once, run sensibly*
   - One runner at a time. Never let the foreground trigger, the background job and a retry timer all work on the same items. Combine the scheduler's unique-work policy with a lease in storage (`offline-queue`).
   - Adapt the pace. Run often only when it matters, and back off when idle. "Every few seconds, just in case" is banned.

   *Survive hostile devices*
   - Detect battery savers and vendor app killers. A heartbeat that the server or the next run checks reveals a stop or delay. Walk the user through the fix in an onboarding reliability check, and log the event.
   - Restart after a reboot and after an app update, if the user had the feature on.

   *Be open about permissions and stops*
   - Explain before each system prompt. Request background-level access only after foreground access. For "only while using" and "approximate" answers, tell the user what will not work (`app-rules`).
   - Attach a reason to every stop. Reasons include: killed, permission lost, battery saver, storage full, signed out. Show it in the app UI and, where others depend on the work, send it to the server. Stale data shows its age and reason. It never shows a false "live".
   - Keep personal data out of release logs. Debug logs hold synthetic data only.

   **Stop if:** any stop path ends with nothing reported.
6. **Write failure-path tests before the happy path.** Each one asserts that the work still happens, or that someone can see the failure (`test-rules` in `check`).
   - No network. The work is queued, retried and delivered, or the failure shows.
   - Process killed mid-run, then restarted. State survives and the work resumes.
   - Two runs start together. Only one does the work.
   - Permission revoked or downgraded. The app surfaces it with a reason.
   - Server error or timeout. Retries are bounded and back off, then a problem becomes visible.
   - Duplicate or out-of-order runs. One effect results. Add a twin test: the dedupe must not eat a genuine second event.
   - The device clock is skewed.
   - Boundary: the run fires exactly at its scheduled time.

   These tests exist to catch one bug: "nothing happened and nobody knows".
7. **Run the platform tests, then native lint.**
8. **Pass on an emulator or simulator.** Script location, network and time where they matter, and force idle mode. Kill the process for real. Swiping the app away does not stop visible foreground work on every OS. The platform notes list the commands. This pass finds logic errors only and never replaces step 9.
9. **Pass on real devices and measure battery.** Use the background rows of `device-test`. Run a release build on a low-end Android, a recent Android and an iPhone: these scenarios: phone locked for 30 minutes, app swiped away, reboot, airplane mode, battery saver on. Compare battery use with the project budget and record the numbers in the change. Does the project run device tests in one batch before release? Then mark these rows open in the PR.

   **Stop if:** a device or battery row is neither done nor listed as open.

## Done when
- [ ] Failure-path tests pass (paste the output) and both platforms build.
- [ ] Core tests pass on both targets.
- [ ] Every stop path reports a reason.
- [ ] Device and battery rows are done, or listed as open in the PR.
- [ ] A change to timing or frequency went through `write-spec` (`ship`) first.

## Never
- Touch safety-critical background work with no failure-path test and no device test.
- Stop silently, or label data "live" when nothing confirms it is fresh.
- Write a rule in two places. If only one platform changes, explain why the other is unaffected.
- Ship a native change as an over-the-air patch. Use a store release (`release` in `ship`).

## Next
- **Comes from:** `build` (`ship`), `fix-bug` (`ship`)
- **Leads to:** `shared-core`, `offline-queue`, `device-test` (`mobile`); `perf-check` (`check`) for battery
