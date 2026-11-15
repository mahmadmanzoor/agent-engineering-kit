---
name: test-rules
description: "What every test must obey, in any stack. Covers structure (arrange/act/assert, one behaviour, literal expectations, no logic), assertion quality, where fakes are allowed, real databases, failure paths first on safety-critical code, proving a test can fail, deterministic time and synthetic data. Also owns the ladder of where mistakes get caught. Use when writing, reviewing or judging tests. Say: '/check:test-rules', 'is this a good test', 'should I mock this', 'flaky test', 'how should this be tested', 'testing rules'."
argument-hint: "[test, test file or question]"
license: MIT
metadata:
  version: "1.0.0"
  model: sonnet
  effort: medium
---

# Test rules

`$ARGUMENTS` is a test, a test file or a question. Judge or guide it against the rules below. With no argument, apply the rules to the tests in the change at hand.

**Run on:** sonnet at medium. The rules are settled, and applying them is narrow work.

## Use it when
- You write, review or repair a test.
- Someone asks whether a fake is allowed, or why a test is flaky.
**Not for:** commands, folders and toolchains (`/check:write-tests`). The red-green loop (`/check:test-first`).

## Before you start
Read AGENTS.md, CLAUDE.md, CONTRIBUTING.md and any testing guide. Find the project's table of allowed fakes, and how integration tests start a real database. Without a table, use the one in step 2 and offer to add it to the testing guide. On facts such as commands and folders, the project decides. On what makes a test trustworthy, these rules decide. If a project rule weakens them, raise it with the user instead of following it quietly.

## Steps
1. **Check the invariants.**
   - **Hard-code every value.** No clock reads, no randomness, no expectation computed by the code's own formula.
     ```text
     good: expect(price(2 nights), 18000)             # 2 x 90.00, worked out by hand
     bad:  expect(price(2 nights), nights * rate)     # repeats the code's maths
     ```
   - **Arrange, act, assert.** Three visible parts and one action. Two actions make two tests.
   - **One behaviour per test, and the name says which**, for example `rejects_an_order_with_more_than_50_lines`. The name alone tells you what broke.
   - **No logic in the body.** No `if`, loop or `try/catch`. For many cases, use a parameterised test or a table.
   - **Exact assertions.** `equals 3`, not `> 0`. The exact error type and code. Assert side effects and absence too. A forbidden caller gets nothing. A retry creates no second booking. A cancelled job sends no email.
   - **Behaviour, not implementation.** Assert only what a caller can observe: shown text, response body, stored row, sent message. Private fields and call order are off limits.
   **Stop if:** a test breaks an invariant. Fix that first.
2. **Check the fakes.** Never mock code you own. Inject the real thing. A view or client test may use an in-memory copy of a repository interface. Fake only what a test cannot run, and give the fake the shape of the real interface.

   | Fake this | With this |
   |---|---|
   | Object storage | Nothing: do not fake it. Run a compatible engine in a container with a fresh bucket per test class. |
   | Sign-in and identity services | A development provider or fake key source |
   | Network calls from a client app | A transport fake that replays recorded real responses |
   | Email, SMS, push, payments | A sender that records what it was asked to send, so you can assert message and recipient |
   | Camera, location, permissions, other device features | A fake of the bridge interface that gives scripted answers |
   | The clock | An injected clock that the test sets and moves forward |

   The project's table is the full list. Never fake databases or caches in integration tests. Start the real engine, give each test class its own freshly migrated database or schema, and use the engine version CI uses.
   **Stop if:** a fake is missing from the table, or code you own is mocked.
3. **Safety-critical code: failure paths first.** This is code where a silent failure can hurt someone, lose money or lose data. Write these tests before the happy path.
   - Timer boundary: fires exactly at the limit, neither a tick early nor never.
   - Duplicate or out-of-order events: one effect, not two. Pair every such test with proof that dedupe does not swallow real events. A genuine second event still fires. A late event after reconnect still arrives, marked late.
   - Server error or timeout: bounded retry, then a fallback or a visible failure.
   - Permission revoked: surfaced, not silent.
   - Process killed mid-flow: state survives.
   - No network: queued and retried, or the person is told.

   AGENTS.md lists which paths count as safety-critical. Alerts, payments, reminders, sync and recovery are just examples. If a path is missing from the list, ask the owner. Each test asserts that the effect happens or that the failure is visible. The bug to catch is "nothing happened and nobody knows".
   **Stop if:** a safety-critical change has no failure-path test.
4. **Prove the test can fail.** Introduce the mistake the test guards: flip `>` to `>=`, delete the auth check, remove the retry. Watch the test fail for the right reason, then revert. The broken line must lie on the path the assertion reads. Feed boundary tests data past the boundary, like 16 minutes old for a 15-minute rule. A test that pins existing behaviour ahead of a refactor may pass first time. Say so in its name and still break it once. Never pin behaviour you think is wrong.
   **Stop if:** a guard on a safety-critical path has no recorded break-it check.
5. **Keep tests deterministic.** Unit tests finish in milliseconds and own their data. Output is identical on every run in every timezone. Run once under a far timezone whenever time logic changes. A flaky test is broken: fix it or delete it, and never retry until green. Wait with bounded polling, not fixed sleeps. Endless animations never settle, so switch them off or advance a fixed time.
6. **Use synthetic data.** "Customer A", "Shop B", generated ids, obviously fake coordinates, reserved phone ranges. Copy the shape of production, never its records.
7. **Integration tests.** Enter through the real entry point (endpoint, job, consumer) with a real database. Seed and clean your own data. Assert isolation: tenant A never sees tenant B, and a forbidden caller gets the status the project defines.
8. **Name the rung.** Each finding, postmortem and lesson names two rungs: where the mistake was caught, and the earliest rung that should have caught it. All other skills use this one ladder:

   **type or compile, lint, architecture test, unit or integration test, CI, plan review, code review, device test, alert, user report**

   Moving a whole class of mistake one rung earlier is worth more than fixing another instance.

## Reject on sight
- Expectations computed in the test
- Skipped or commented-out tests
- Tests that pass with or without the feature
- Mocks of your own code
- Branches or loops in tests
- Retries to hide flakiness
- "Not null" where a value was the point
- Fixed sleeps
- Real personal data
- A safety-critical change with no failure-path test

## Done when
- [ ] A read-through shows each test in scope meets steps 1, 2, 5 and 6.
- [ ] Every fake appears in the project's table.
- [ ] Each safety-critical guard has a break-it check with its failing output.

## Never
- Weaken or delete a test just to get a change through. A test that was wrong gets its reason written in the change.
- Ignore a rule that turns out wrong. Change it in the project's testing guide and record it with `/kit:lesson`.
- Give agent-written tests an exemption. Every test follows the rules.

## Next
- **Comes from:** `/check:write-tests`, `/check:test-first`, `/check:review-code` (check), `/ship:build` (ship), `crew:test-writer` (crew)
- **Leads to:** `/check:write-tests` for commands and folders, `/check:test-first` for the loop
