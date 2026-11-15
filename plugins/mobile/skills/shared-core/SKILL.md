---
name: shared-core
description: "Put every native rule in one core that Android and iOS share, and leave thin shells on each side to wire the OS. Defines what the core holds, a quick check for whether code is a decision, adapters that hand back failures, how to cross the language boundary, where threads live, and lint that keeps the core pure and the shells decision-free, with an empty baseline. Use when native logic is shared, should be, or differs per platform. Say: '/mobile:shared-core', 'shared core', 'the platforms disagree', 'rule lives in two places', 'functional core imperative shell'."
argument-hint: "[native change, file needing a home, or diff]"
license: MIT
metadata:
  version: "1.0.0"
  model: opus
  effort: medium
---

# Shared core, thin shells

Use the core and shell split on `$ARGUMENTS`: a native change, a file that needs a home, or a diff. Without an argument, use it on the change you are making.

**Run on:** opus at medium. A rule written twice drifts apart, and safety-critical background code cannot afford that.

## Use it when
- Native logic must act the same on both platforms.
- You are about to write one rule in native code on each platform.
- The platforms already disagree: one retries, the other gives up.

**Not for:** placing app-layer code (`app-rules`), or the background job workflow (`background-work`).

## Before you start
Read `AGENTS.md`, `CLAUDE.md`, decision records and the READMEs in the native folders. Check whether a shared core exists, and what it is built with. Open [references/kmp.md](references/kmp.md). For a shared native library, or a core written in the app framework's own language, open [references/other-cores.md](references/other-cores.md). Collect the commands for core tests on both targets, platform tests and native lint.

There is no core yet, and the change would add a rule on both platforms? Raise a design question first (`plan-review` in `ship`, `decision` in `kit`). Do not write the rule twice.

An app built with a cross-platform framework may use the framework's own language as its core. The same demands hold there. The code is pure, imports no UI and no plugins, takes time and OS facts as arguments, and returns failures as values. Native code keeps only OS glue. Go native only for rules that must run when the framework engine is absent. Record which option the project takes.

## Steps
1. **Sort each piece of logic into core or shell.** Five parts exist. The examples use a notes app that syncs in the background.
   - **Core.** Holds every rule: what a server answer means, retry timing, what blocks work, what is kept or dropped, which status shows, sampling policy, problem codes, wire models, and the interfaces the rules need. It may use interfaces it declares. It receives time and OS facts (battery, charging, permission, network) as parameters. It must not import platform or I/O code, read the clock, start threads, log personal data, or throw across an interface.
   - **Platform bits of the core.** A few primitives the shared language lacks, such as a lock or an atomic. They may use the platform standard library. They hold no rules.
   - **Adapters.** They implement the core's interfaces on top of the OS: transport, secure store, queue database, timers. They may call the OS and must turn OS failures into the interface's failure value. They must not set policy, and must never answer "empty" or "done" for a failure.
   - **Shell.** Lifecycle and wiring: services, OS callbacks, boot and update receivers, schedulers. It reads OS facts and passes them in. It applies the core's answer with an exhaustive match, and hops threads. It must not decide. Shell code never compares a problem code or a state.
   - **Bridge.** The app-to-native contract, as generated bindings. It converts bridge types to core types. It holds no logic, and nobody edits generated files by hand.

   How to tell what is a decision:
   - Any branch whose outcome changes app behaviour or display is a decision. Think of recording, blocking, starting, restarting, clearing, reporting, retrying, and choosing a status. Decisions belong in the core, including ones that only one platform needs.
   - A shell keeps only a fact about one OS API, for example which broadcasts mean "rebooted", or how to read a permission.
   - The quick test: if the other platform would ask the same question, it is a core rule.
   - When the OS forces two mechanisms (an interval request on one platform, a stream to filter on the other), the core holds both halves, computed from the same numbers. A doc comment says so.
   - A change to sampling, upload timing or reporting changes how fresh users' data is. Send it through `write-spec` (`ship`) first, and say how a "running but degraded" state gets reported.

   **Stop if:** you are writing a policy branch in shell code. Move it to the core and test it.

2. **Write the core to cross the language boundary safely.**
   - Throw nothing across an interface. An interface the shell implements returns its failure, such as null for "unreadable" or false for "could not write". An entry point the shell calls catches everything and returns an outcome value. Any sequence both shells would write, such as a stop or a session switch, lives in the core.
   - Name enum entries so the binding maps them cleanly (see the reference). On the far side, a match over a core enum needs a default branch.
   - Avoid tuples. Avoid default arguments that callers depend on. Use small named value types, and expose constants a shell needs.
   - Learn how integers and nullable types map. Epoch times should be 64-bit integers, and measurements floating point. Confine each platform's conversions to a single bridge file.
   - Core names must not collide with names the bridge generates.

3. **Keep threads in the shells.**
   - The core owns no threads. Its calls are safe from the one worker thread or queue the shell uses. State shared across threads is guarded by the core's own lock or atomics.
   - Follow whatever threading model a shell's existing files use. New components may adopt structured concurrency with a scope they own and cancel. Ban global scopes, two models inside one type, and blocking the main thread.
   - The core supplies delays and retry intervals, so tests can control them.

4. **Handle errors and keep it safe.**
   - Never drop a record silently (`offline-queue`). A failed send keeps the record and retries. If the store cannot be read, end the run with a retry. Do not report "done".
   - Report every blocking condition to the app and to the server.
   - Catch the narrowest type. A broad catch is allowed only at a shell boundary, and it must report. Empty catches and force unwraps, or not-null assertions, are banned in new code.
   - Keep personal data out of logs and out of a type's string form.

   **Stop if:** an adapter turns a failure into "empty" or "done".

5. **Test and lint.**
   - Test core logic once, in the core's shared tests, using fakes of the core's own interfaces, with time and OS state as parameters. Run the tests on both targets. A test that passes on one target and fails on the other exposes a platform difference inside the core. Repair it there.
   - Adapter tests stay native. They cover the queue database, secure store, retry timer and bridge mapping. An unreadable store yields a failure value, never empty. Rows written by an older build, as real old bytes, still read.
   - Lint with no baseline:
     - core purity: core files import only the shared standard library, with no platform, I/O, clock, thread or console API;
     - decision-free shells: shell code never compares problem codes or states for equality;
     - size: production files have at most about 320 lines and 3 top-level types of one concern. Generated files are skipped.
   - CI runs formatting and the platform linters.

## Done when
- [ ] New rules live in the core with tests that pass on both targets (paste the output).
- [ ] Shells gained only OS facts and wiring.
- [ ] Core interfaces return failures and never throw. No adapter hides a failure.
- [ ] Generated bridge files are untouched. The contract changed at its source and both sides were regenerated.
- [ ] Adapter tests and native lint pass.
- [ ] Logs contain no personal data, and file sizes respect the limits.
- [ ] A device pass is planned on both platforms (`device-test`).

## Never
- Write one rule in two places. If only one platform changes, say why the other is unaffected.
- Add a lint baseline, or an exception because of precedent.
- Ship a native change as an over-the-air patch. It goes out in a store release (`release` in `ship`).

## Next
- **Comes from:** `background-work`, `home-widget`, `app-rules` (`mobile`); `build` (`ship`); `review-code` (`check`)
- **Leads to:** `device-test` on both platforms; `decision` (`kit`) to adopt a core
