---
name: write-tests
description: "Produce tests for code you point at: a file, feature, behaviour or diff. Build a behaviour list first (failure paths ahead when safety matters), pick the cheapest level that proves each item, write to the test rules, run one test and then the area, and report red and green evidence with break-it checks. References cover the common toolchains. Use for adding tests to new or old code. Say: '/check:write-tests', 'what tests are missing', 'cover this with tests', 'test this', 'add tests', 'write tests for'."
argument-hint: "[file, feature or behaviour, or nothing for the branch diff]"
license: MIT
metadata:
  version: "1.0.0"
  model: sonnet
  effort: medium
---

# Write tests

`$ARGUMENTS` names what to test: a file, class, feature or behaviour. Given nothing, test whatever the current branch changes relative to main. Read `/check:test-rules` first if you have not yet this session. Here you get the how.

**Run on:** sonnet at medium. Scoped work, and running the tests checks it.

## Use it when
- New or existing code needs tests, or you need to find what is missing.
**Not for:** the one-test-at-a-time loop (`/check:test-first`). Judging whether a test is good (`/check:test-rules`).

## Before you start
- Read AGENTS.md, CLAUDE.md and CONTRIBUTING.md for test commands, folders and naming.
- Find the stack in the manifest and CI file, then open its reference: [csharp](references/csharp.md), [python](references/python.md), [node](references/node.md), [jvm](references/jvm.md), [flutter](references/flutter.md), [swift](references/swift.md).
- Before writing a helper, look for one already there and reuse it. Typical ones: the integration host, database fixture, fake clock, recording senders, UI pump helper.
- Commands and folders from the project win. The reference only fills gaps.

## Steps
1. **List the behaviours.** Take them from the acceptance criteria, the design's states or the diff. Order them like this: happy path, then variations, then edges (empty, a single item, exactly on a limit, just past it, maximum size), then errors (invalid input, a forbidden caller, network or server failure). In safety-critical code, failure paths go first (`/check:test-rules`, step 3). Search the test folders for each behaviour's key words and skip what is covered.
   **Stop if:** an entry is not something a caller can observe. Reword it.
2. **Choose the lowest level that proves each behaviour.**

   | If it is | Test it as |
   |---|---|
   | Platform code: background work, widgets, OS bridges | A native unit test where possible, plus `/mobile:device-test` steps |
   | The exact look of a key screen | A screenshot test |
   | A screen with several states | One UI test per state, checking content and accessibility labels |
   | Client logic: formatters, view models, repositories | A unit test with in-memory repository or transport fakes |
   | A job, timer or consumer | A unit test on a fake clock, plus one integration test that enters where the job does |
   | A contract, an authorisation rule or persistence | An integration test through the real entry point, on a real database |
   | A pure rule: a limit, a calculation, a state change, a permission matrix | A unit test of the domain |

   Add one integration test for every seam.
3. **Write the tests.** Follow `/check:test-rules`. Read time from the injected clock. Use synthetic data. In integration tests, swap out only true externals, through the project's host. For forbidden callers, use the statuses the project defines (`/server:add-endpoint`, server). Update screenshots only for changes you intended, and view the image diff first.
4. **Run them.** Start with the single new test. It must fail before the code exists, and for the expected reason. Next run its file, then the area, then the whole suite before you commit. Do the break-it check for each guard on a safety-critical path.
   **Stop if:** you never saw a new test fail for the right reason, or the area suite is not green.
5. **Report.** List the tests added (file and behaviours). Give the command and result line for red and for green. Name the break-it checks you ran. Say what remains untested and why, for example "needs a real device, so a `/mobile:device-test` row".

## Done when
- [ ] A written behaviour list exists, and each entry has a test or a stated reason.
- [ ] Each new test was seen red and then green, with command and result line.
- [ ] The area suite passes.
- [ ] Break-it checks are recorded for safety-critical guards.

## Never
- Weaken an existing test so new code can pass.
- Build a new helper when an old one works. If a shared one is truly needed, put it where the project keeps test support code.
- Claim "tests pass" with no command and output to show.

## Next
- **Comes from:** `/ship:build`, `/ship:fix-bug` (ship), `crew:test-writer` (crew), a review finding
- **Leads to:** `/check:test-first` for the loop. `/ship:commit-check` (ship).
