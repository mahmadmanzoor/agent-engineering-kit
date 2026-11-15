---
name: test-first
description: "Grow a feature through tiny red-green-refactor cycles. Take the next behaviour from the test list, write one failing test, confirm it fails for the right reason, write just enough code, tidy up on green, commit, repeat. Also lists design warning signs and the few exceptions. Use when implementing or fixing any behaviour. Say: '/check:test-first', 'red green refactor', 'TDD this', 'test first', 'failing test first', 'build this test-driven'."
argument-hint: "[what to build: behaviour, criterion or issue]"
license: MIT
metadata:
  version: "1.0.0"
  model: sonnet
  effort: medium
---

# Test first

`$ARGUMENTS` is what to build: a behaviour, an acceptance criterion or an issue. Build it one test at a time. With no argument, use the next entry under "Tests to write first" in the current issue.

**Run on:** sonnet at medium. Small steps, and a test run checks each one.

## Use it when
- You are implementing or fixing any behaviour.
**Not for:** what makes a test good (`/check:test-rules`). Commands, folders and toolchains (`/check:write-tests`).

## Before you start
Read AGENTS.md or CLAUDE.md for the test commands. The one you need most runs a single test. Read the issue or spec: its acceptance criteria and test list give the order of work. Read the code around the change, plus the rules of its layer (`/ship:code-placement`, ship).
**Stop if:** you cannot run one test on its own, or there is no ordered test list. Sort that out first.

## Steps
1. **Choose one behaviour.** Work down the list: the issue's own tests, then edge cases, then error cases. In safety-critical code, start with the failure paths (`/check:test-rules`, step 3). Never more than one behaviour at a time.
2. **Red.** Write a single test and run just that one. It has to fail for the reason you predicted, which is an assertion on the missing behaviour. A typo, a missing fixture or an accidental compile error is the wrong reason. Paste the failure line. One case is fine: a compile error may serve as the first red if the type or function truly does not exist yet. Add an empty shell, then rerun until the failure is the assertion.
   **Stop if:** it fails for any other reason, or it passes. A pass means the behaviour already exists or the test asserts nothing. Run the break-it check from `/check:test-rules`, step 4.
3. **Green.** Write the smallest code that passes this test. Returning a hard-coded value is fine if the next test will force the general case. Run the test, then its whole file.
4. **Refactor.** All tests are green, so you may remove duplication, improve names, and move rules from edge layers into the domain. Rerun the area's tests after every move. Add no new behaviour now.
5. **Commit** each time a meaningful behaviour is complete (`/ship:commit-check`, ship). Then return to step 1.

## Signs your design is wrong
- Making it green needs a big chunk of code. The test covers too much, so split the behaviour.
- You want to mock a class you own. Inject the real one instead. Fake only the boundaries listed in `/check:test-rules`.
- The test is awkward to write. Too many dependencies, or logic in an edge layer. Fix the design, not the test.

## Exceptions
- **Pinning tests** written before a refactor may pass first time. Label them as such.
- **Layout copied from a design:** first test each state's content and accessibility. Compare the look afterwards with screenshots (`/mobile:design-to-screen`, mobile; `/web:add-page`, web).
- **Platform code CI cannot run:** do the portable logic test-first. Write the device steps before the change and run them after (`/mobile:device-test`, mobile).
- **Config, docs and generated code:** do not invent a failing test. Use the checks they come with.

## Done when
- [ ] Each cycle shows its red output (an assertion on the new behaviour) and a green run of that test and its file.
- [ ] After the final refactor the area's tests pass, shown by the command and its result line.
- [ ] No behaviour exists that a red test did not ask for.

## Never
- Write a batch of tests and then all the code.
- Write code that no red test requested.
- Edit a test to fit the code, unless the test was wrong. Say why when you do.
- Run the full suite while cycling red and green. Run the single test.

## Next
- **Comes from:** `/ship:build`, `/ship:fix-bug` (ship)
- **Leads to:** `/ship:commit-check` (ship) per finished behaviour. `/check:write-tests` for commands. `/check:test-rules` for the rules.
