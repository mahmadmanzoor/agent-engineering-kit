---
name: server-rules
description: "Place and write server code the right way on any stack: layers (edge, application, domain, persistence, adapters, workers), thin edges, two kinds of validation, errors as values, data access, transactions and locks, time, logging without personal data, config and secrets, one retry owner, performance and data integrity. Use when you write or review server code. Say: '/server:server-rules', 'service layer', 'business logic in the controller', 'where does this go in the backend', 'how do I structure this endpoint', 'N+1', 'transaction'."
argument-hint: "[a server change, a file to place, or a diff]"
license: MIT
metadata:
  version: "1.0.0"
  model: opus
  effort: medium
---

# Server rules

Place and check server code for `$ARGUMENTS`. If empty, use the change in hand.

**Run on:** opus at medium. Wrong placement, missing access checks and bad transactions cost data and trust.

## Use it when
- You write or review server code and need to know where each part goes.
- A handler holds queries, rules or transactions.
**Not for:** the reasons behind the layers (`ship:code-placement`). A new endpoint, migration, job or upload has its own skill in this plugin.

## Before you start
Read `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, the placement table and the decision records. Find the stack from the manifest and open the matching file in the `references/` folder (one file per stack). With no match, map these rules onto the stack's own habits and say so. Find the modules, architecture tests, test host and commands. The project's names win; names here are placeholders.

## Steps
1. **Place each file.** Use this table.

   | Layer | Job | Must not |
   |---|---|---|
   | Domain | Entities, value objects, invariants, limits, pure rules | Touch I/O, the database, HTTP, logging, clock, randomness, crypto, file formats |
   | Persistence | Data context, mappings, reusable queries, locks, migrations | Decide business rules |
   | Application | One service per area. Each public method is one use case | Use web types, status codes or JSON |
   | Edge | Bind input, validate shape, call one use case, map the result | Hold queries, transactions, locks or rules |
   | Adapters | Implement ports over vendors (email, push, payments, storage) | Decide whether to act |
   | Workers | Thin, idempotent jobs that call application services | Hold rules |

   Concept test: would a product person recognise the type? An order, a booking: yes, domain. A header parser, an HMAC: no. Put it behind a port with an adapter. Ports for outside systems live in the application layer. No interface for code you own.
   **Stop if:** a file fits no row. Treat it as a design question and raise it.
2. **Keep edges thin.** About 15 lines. Bind, validate shape, pass the caller's id as a plain value, call one use case, map the result. The edge authenticates. The use case authorises.
3. **Split validation in two.** Shape (required, length, format) lives at the edge in one validation unit per area, using the domain's constants. Invariants live in the domain. Checks that need stored state (counts, uniqueness, membership) belong to the service, which returns an error value.
4. **Return errors as values.** An expected failure has a kind and a stable code. The edge maps kind to status and code to a problem type. Clients key on the code. Exceptions are for bugs and broken infrastructure. Catch a specific type and recover visibly, or rethrow. Safety-critical paths never swallow an error.
5. **Authorise in the use case.** One access unit per resource kind. A non-member gets not found. A member without the role gets forbidden, or the project's stated rule. Filter queries by tenant id. Do not trust an id taken from the URL alone. Never cache a permission decision.
6. **Use the data layer well.** One unit of work per request or job, never shared across threads. Project reads to the needed columns. Load, call domain methods, save for writes. Use set-based statements for bulk changes and check the row count. No generic repository over an ORM. No lazy loading, no N+1.
7. **Own the transaction in the use case.** Begin, take locks in the documented order, re-read state and rights under the lock, save, commit, then notify. One save needs no explicit transaction. Never call HTTP, caches or brokers while holding a lock. Test races with a gate, never a sleep.
8. **Handle time and I/O.** Time comes from an injected clock, passed in as `now`. Store UTC. Every I/O call has a timeout. Stay async end to end where the stack is async.
9. **Log without personal data.** Structured templates. Never log coordinates, addresses, phones, emails, tokens, codes or names. Ids are fine in logs, never as metric tags. `check:security-review` owns this rule.
10. **Configure once.** Use typed options per feature and validate them at start. Read raw config only in the composition root. Give each purpose its own secret, and never fall back to a key meant for something else. Add each new setting to the example env file. Code that exists for development must be unreachable in other environments.
11. **Call out safely.** Create each outbound client once, in one place per vendor. Idempotent reads get a total timeout, retry with backoff and jitter, and a circuit breaker. A client never retries a send (email, SMS, push, payments). The job that sends is the one retry owner, with an idempotency key. Caches fail fast and degrade.
12. **Keep background work thin.** First ask if a stored time is enough. A job is idempotent, records what it sent and never swallows failures. A loop makes one application call per pass. Details: `server:add-job`. Uploads: `server:add-upload`.
13. **Write it fast.** No database or cache call in a loop. Filter, sort, count and page in the database. Use `exists`, not `count > 0`. Bound every growing list with a limit and cursor paging. Insert in bulk. On a large table, index every filter, join and sort, and read the plan. Add a cache only after measuring a need, and name who invalidates it.
    **Stop if:** a changed query, hot path or list has no plan or query count in the PR. Add the number (`check:perf-check`).
14. **Model data for integrity.** Normalise by default. Let the database enforce what it can: `NOT NULL`, foreign keys with explicit delete behaviour, unique indexes, `CHECK` ranges. Domain limits and constraints share one constant. Keys are UUIDs, times are UTC with zone, enums are short text, units sit in column names. Every invariant has a concurrency strategy: a lock, an optimistic version or a unique index. Never check-then-insert without one. Personal data has one home per kind, a retention rule and deletion that reaches every identifying row.
15. **Enforce with tests.** Write architecture tests as allowlists with empty baselines. They cover domain imports, raw bytes kept out of the domain, edges that never reach persistence, raw config reads and direct clock reads. Run analyzers at the recommended level and treat warnings as errors. Put each suppression at the offending line, with a reason. Ship every new structural rule together with its test.

## Done when
- [ ] Each file sits in one row of the table, and its imports stay inside that row.
- [ ] Edges hold no data access, transaction, lock or rule.
- [ ] A non-member gets not found and a member without the role gets forbidden, shown by a test.
- [ ] No database or cache call sits in a loop. New filters have indexes, and the PR holds the plan or query count.
- [ ] Architecture tests and analyzers are green (command and output shown).

## Never
- Never loosen a safety, privacy or testing rule so that code fits a convention.
- Never excuse a violation with "the old file does it".
- Never cache a permission decision.
- Never let a client retry a send.
- Fix a wrong convention in its doc and its test (`kit:new-skill`), not by ignoring it.

## Next
- **Comes from:** `build` and `plan-review` (ship), `review-code` (check)
- **Leads to:** `add-endpoint`, `add-migration`, `add-job`, `add-upload` (server); `ship:code-placement` for the why; `kit:decision` for a new pattern or library
