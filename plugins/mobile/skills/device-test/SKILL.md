---
name: device-test
description: "A real-phone test pass for any mobile change that affects background jobs, offline use, notifications, widgets, permissions or battery drain. Picks three devices, uses release builds and test accounts, runs the checklist, measures battery against the budget, puts a results table in the PR, and files one bug per failure. A project may batch device tests into one pre-release pass, but may never skip them silently. Use before you merge or release something a simulator cannot prove. Say: '/mobile:device-test', 'test on a real phone', 'battery test', 'does it survive a kill', 'low-end android check'."
argument-hint: "[PR, branch or feature under test]"
license: MIT
metadata:
  version: "1.0.0"
  model: sonnet
  effort: low
---

# Device test

Work through the checklist rows that fit `$ARGUMENTS`, which is a PR, branch or feature, and log each outcome. No argument means the PR for the branch you are on.

**Run on:** sonnet at low. This is a checklist, and each row ends in something you can see.

An emulator finds logic errors. Only real hardware running a release build shows background limits, vendor battery killers, notices on a locked phone and true battery drain.

## Use it when
- A change touches background work, offline behaviour, notifications, widgets, permissions or battery.
- You are about to merge or release something a simulator cannot prove.

**Not for:** logic tests (`write-tests` in `check`), or detailed battery profiling (`perf-check` in `check`).

## Before you start
Read `AGENTS.md`, `CLAUDE.md`, the device list, and the performance and battery budgets. Learn when the project wants device tests: on every PR, or in one batch before release. Look up the release-build command for each platform, and which test accounts and environment to use.

## Steps
1. **Choose three devices.**
   - *Low-end Android.* 2 to 4 GB of RAM and aggressive battery management, such as a budget phone from a maker known for killing apps. It shows a slow CPU and background kills.
   - *Recent Android.* A current flagship. It is the reference.
   - *iPhone.* A model a few years old, on the current iOS. It shows background limits and notification behaviour.

   Install a release or profile build. Debug builds act differently in the background. Sign in with test accounts only, and feed the app synthetic data. Name each device by serial in every command.

   **Stop if:** the build is a debug build, or the account holds a real person's data.

2. **Optionally warm up on an emulator or simulator.** Script a network drop, forced idle, a true process kill, and location or time changes where useful. The commands sit in the `background-work` references. This pass checks logic only and never counts as a device test.

3. **Run the rows.** For each device, mark pass, fail or n/a. Add rows the change needs. Remove no row that applies.

   *Onboarding and permissions*
   - [ ] Fresh install: every permission is explained first, and only then does the system prompt appear.
   - [ ] Try deny, "only while using", "approximate", and a later revoke in settings. Each time the app names what no longer works and how to repair it.
   - [ ] Camera and photos, where used: an explanation comes before the first prompt, and a denial leads to a fix. On iPhone, limited photo access works with the shared photos and lets the user change the selection.

   *Background work*
   - [ ] The job runs while the app is in the background, and slows down when idle as designed.
   - [ ] Swipe the app away or lock the phone for 30 minutes. The job still runs, or the screen shows how stale it is and why.
   - [ ] After a reboot and after an app update, with the feature on, it resumes.
   - [ ] With battery saver or a vendor optimiser on, the app detects it and shows the fix.

   *Offline and uploads*
   - [ ] Airplane mode for 10 minutes while the user creates data. On reconnect everything uploads, nothing is missing, nothing is duplicated.
   - [ ] Offline for days (move the clock, or leave it overnight) with several records and attachments. On reconnect all of it uploads exactly once.
   - [ ] Kill the app while offline. After the next launch the data still goes up.
   - [ ] A large upload is force-stopped halfway. After a restart it carries on, and the server ends up with a single record and one copy of each file.
   - [ ] Throttled or dropping network, and a captive portal (Wi-Fi that serves a login page). No false "sent" status appears. The app retries and makes no duplicates.
   - [ ] Storage nearly full. The app turns down a new attachment with a clear message, and queued data is untouched.

   *Notifications*
   - [ ] Alerts arrive on a locked phone inside the budget. Tapping one lands on the correct screen.
   - [ ] What shows on the lock screen follows the privacy setting.
   - [ ] A duplicated event yields one alert. A genuine repeat still yields a new one.

   *Widgets and tiles, if changed*
   - [ ] Add the widget, view each state, use each action, check lock-screen privacy. After the app is killed the widget turns stale and says why.

   *Battery, against the project budget*
   - [ ] One hour of active use: record the percent used.
   - [ ] One hour idle with the feature on: record the percent used.

   *Accessibility smoke test*
   - [ ] At the largest font size the main flows work and nothing is clipped.
   - [ ] With a screen reader (TalkBack or VoiceOver), the user can complete and cancel the main action and any urgent action.

4. **Put the results in the PR.**

   ```markdown
   ## Device results
   | Device (model, OS) | Locked 30 min | Offline sync | Battery, 1 h active | Battery, 1 h idle |
   |---|---|---|---|---|
   | Budget Android (model, version) | pass | pass | 3.6 % | 0.9 % |
   | Flagship Android (model, version) | pass | pass | 2.9 % | 0.5 % |
   | iPhone (model, iOS) | fail: sync stopped at 18 min, <bug link> | pass | 3.1 % | 0.6 % |
   ```

   File a bug (`file-bug` in `ship`) for each fail, or fix it in the same PR before the release goes out.

   **Stop if:** an applicable row has no result and is not listed as open with a reason.

## Done when
- [ ] Every row that applies has a result on each device, or appears as open in the PR and in the pre-release pass.
- [ ] Each fail links to a bug or to a fix in the PR.
- [ ] Battery figures appear next to the budget.

## Never
- Mark a device row as passed on the strength of an emulator run.
- Drop a row quietly. If you did not do it, list it as open and give the reason.
- Use a real person's account or data, or act on a device nobody asked you to use.
- Release background, notification, widget or battery changes while device rows are still open.

## Next
- **Comes from:** `background-work`, `offline-queue`, `home-widget` (`mobile`); `build` (`ship`)
- **Leads to:** `file-bug` (`ship`) for each fail; `release` (`ship`) requires it; `perf-check` (`check`) for battery detail
