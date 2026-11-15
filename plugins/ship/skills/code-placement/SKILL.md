---
name: code-placement
description: "Rules that hold on any stack for deciding where code lives and what clean code looks like. Each layer has one job, domain code passes a concept test, dependencies point inward, ports appear only at real boundaries, errors are explicit, every fact has one source, every technical kind of code has one home, and structure is enforced by allowlist architecture tests with empty baselines. Use to place code, review a design, or judge whether code is clean. Say: '/ship:code-placement', 'where should this live', 'which layer is this', 'is this clean', 'SOLID', 'separation of concerns', 'too much abstraction', 'utils folder', 'architecture test'."
argument-hint: "[a question, a design, or a diff]"
license: MIT
metadata:
  version: "1.0.0"
  model: opus
  effort: medium
---

# Code placement

Use these principles on `$ARGUMENTS`: a placement question, a design to check or a diff. With no argument, apply them to the change in hand. The project's own convention skills (`server-rules`, `app-rules`, `web-rules`) say how. This one says why.

**Run on:** opus at medium. Placement takes judgment, and a bad home gets copied by the next change.

## Use it when
- You need to decide where some code belongs.
- You are reviewing a design or asking whether code is clean.
- Something smells over-built, or a folder has become a dumping ground.

**Not for:** bug-hunting in a whole diff (use `review-code`, check plugin).

## Before you start
1. Read AGENTS.md, CLAUDE.md, CONTRIBUTING.md and any decision records (`docs/decisions/`, `docs/adr/`).
2. Look for the project's placement table and its architecture tests or import lints. If they exist they are the concrete answer, and this skill explains them.
3. If there is no table, answer from the rows in step 2 and offer to add one. A template is in [references/placement-table.md](references/placement-table.md). `new-repo` (ship) installs it in a fresh repo.

On facts (paths, names, commands) the project wins. If a project rule contradicts a principle here, tell the user so one side gets corrected. Do not follow neither in silence.

## Steps
1. **Apply the principles.** Check the code against each.
   1. **Each layer has one job.**
      - *Edge* (handler, consumer, job entry, screen, CLI command): parses input, authenticates, hands the caller to one use case, translates the result. It holds no business rules, authorisation decisions, queries, transactions or retries.
      - *Use case* (application service, view model): decides what happens when someone does X. It authorises the caller through the one access-check unit, then runs rules, data and effects in order. It knows no status codes, wire formats, widgets or SQL.
      - *Domain* (entities, value objects, pure rules): answers "is this allowed?" and "what is the new state?" using business concepts only. No I/O, clock, logging or randomness. Technical concerns stay out even when pure: file formats, encodings, parsing, crypto.
      - *Data and adapters* (repositories, API clients, platform services): store, fetch and send. They never decide what is allowed.

      Split a rule across two layers and the halves drift. Bury it in the wrong layer and you cannot test it alone.
      **Concept test.** Would a product owner or support agent recognise it as one of the product's rules? "A booking holds at most 8 guests" passes. "A PNG starts with an 8-byte signature" or "parse this CSV" fails. Put technical code in an adapter even if it is pure. Purity buys testability, not a place in the domain.
   2. **Dependencies point inward:** edge, then use case, then domain. Add a port (interface) only where the far side is outside the process and could be swapped or faked: providers, payment gateways, identity, the OS, another service, the clock. Code you own inside the process gets no interface.
   3. **SOLID in practice.** A unit changes for one reason. A new case means a new type or table row, not an edit to five switches. A fake behaves like the real thing (same errors, same order). Interfaces are small and shaped by their caller.
   4. **Small, cohesive units.** Let tests enforce what a machine can count: lines per file, types per file, constructor parameters. Review the rest by eye. Functions stay near 40 lines. Aim for at most about 5 injected dependencies. A sixth signals a second job, so split the unit. Bundling parameters into one object only hides it.
   5. **No dumping grounds without rules.** A `utils` or `shared` folder is acceptable with three things: a stated purpose, an allowlist of contents, and a test proving it never reaches back into the features that depend on it. Without them, put a helper beside the type it serves.
   6. **Errors are explicit.** Outcomes you expect (not found, denied, expired, conflict, full) travel as values, using a result type or a closed set of cases. Exceptions mean bugs or broken infrastructure. A catch either recovers visibly or rethrows. On safety-critical paths, failures always surface. Take the project's list, or default to any place where silent failure could hurt a person, lose money or corrupt data. If unsure, treat it as safety-critical and ask.
   7. **Testable from the start.** Pass dependencies through the constructor or container. Inject the clock, ids and randomness. Create seams only at real boundaries (`test-rules`, check plugin).
   8. **One source of truth.** Keep each of these in exactly one place: API contract, design tokens, strings, limits, wire names. A client may copy a server limit for quick feedback, but the server decides, and the client handles its refusal.
   9. **Names tell the truth.** A path should predict the file's contents. Role suffixes stay consistent. Comments explain why, not what.
   10. **Tests enforce rules, so memory need not.** If a machine can check a structural rule, write it as an architecture test or lint. State layer rules as allowlists. Start baselines empty. If a rule cannot be met yet, keep a list that only shrinks, with a reason per entry. "The old code does it" is never an exception. See [references/architecture-tests.md](references/architecture-tests.md).
   11. **Speed by design, shown by numbers.** No query or network call inside a loop. Lists are bounded. Work happens once. Heavy work stays off the UI thread. A hot-path change ships with a measurement (`perf-check`, check plugin).
   12. **Start simple.** No flag, parameter, interface or setting that nobody requested. Repeated knowledge (a rule, limit or wire name) is a bug. Repeated code shape is fine until the third copy. Prefer composition to inheritance.
   13. **Thin vertical slices.** Ship one user-visible behaviour end to end, then start the next. Refactoring is a separate change that keeps behaviour fixed and tests green on both sides.
2. **Find the home for each kind of code.** Agents copy whatever sits nearby, so every technical kind of code needs one declared home. Rename to fit the stack. Each entry reads: kind, then home, rule and check.
   - **Business rules:** the domain. Concept test; no I/O, clock or logging. Check: allowlist test on domain imports.
   - **Use case orchestration:** application service or view model. One method per use case, which owns the transaction and notifies after commit. Check: review, and edges call one use case.
   - **Input shape validation:** one unit per area, at the edge. It uses the domain's constants, never numbers of its own. Check: field-error maps are built only there.
   - **Secrets and crypto:** one owner per purpose, each with its own config validated at start. Never reuse another purpose's key, never fall back to another secret. Check: crypto APIs appear only in the owners.
   - **File and object storage:** one generic storage port, one adapter per provider, no per-feature storage class. Check: storage SDKs appear only in the adapter.
   - **File formats, parsing, encodings:** an adapter beside its port, never the domain. Check: the domain handles no raw bytes.
   - **Raw request bodies and uploads:** one upload reader at the edge that takes the type from the bytes and caps size. Handlers never read a raw body. Check: test.
   - **Rate limits:** one limiter folder with numbers in config. Each limiter says whether it fails open or closed. Check: limiter types appear only there.
   - **Outbound calls:** the adapter's client config. One retry owner per path. A non-idempotent send is never retried without an idempotency key. Check: review.
   - **Long-lived loops (reconnect, reconcile, outbox dispatch):** a coordinator or worker that makes one use-case call per pass and holds no rules. Check: repositories never import coordinators.
   - **Scheduled jobs:** one scheduler plus thin job entries that each call one use case (`add-job`, server plugin). Rules: a single scheduler instance, even during deploys; idempotent jobs; rows claimed with a lease; a unique sent-ledger key per effect; access re-checked at run time; times taken from the stored zone. Check: jobs call one use case; a race test; a dedupe test.
   - **Outbound notifications:** one notification port, one adapter per channel, templates in one place. Honour preferences and unsubscribe, use a unique ledger key, re-check access at send time, keep personal data out of logs. Check: vendor SDKs appear only in adapters.
   - **File uploads and attachments:** the upload reader plus the storage port (`add-upload`, server plugin). Use presigned or multipart upload, size caps, type from bytes, and strip metadata. A parent record counts as complete only after every attachment is confirmed. Client-chosen ids make retries harmless. Check: a test for an incomplete parent.
   - **Code shared by two or more features:** a shared module that follows principle 5 and never imports a feature. Check: shared code imports no feature.
   - **Wire contract:** a contract file plus mappers at the boundary. Generated types never leave the data layer. Check: import test.
   - **Wire enums:** one wire-name mapping, and the wire spelling lives only there. Check: test.
   - **Configuration:** typed options per feature, validated at start, with no raw lookups outside the composition root. Check: test.
   - **Time:** an injected clock, with no clock reads outside the composition root. Check: test.
   - **Local wall-clock times:** store the zone id and the local time, and compute instants in the domain. Never store a fixed UTC offset. Test both DST changes.
   - **Expected failures:** result values per area, mapped to protocol errors at the edge. Clients key on a stable error code, not the message. Check: contract test.
   - **Authorisation:** a single access-check unit for each resource kind, invoked from the use case. A non-member gets not-found. A member without the role gets forbidden (or whatever the project's rule says). Never cache a decision past a membership change. Check: integration tests with forbidden and removed callers.
   - **Retry-safe creates:** the use case plus a unique constraint. Offline-created records carry a client id as a permanent unique key, and a repeat returns the original. Check: the same id twice gives one row and the same response.
   - **Transactions and concurrency:** the use case. Lock or version every invariant that spans rows. Never check-then-insert without one. Check: race tests.

   If a kind of code fits no entry, that is a design question. Add the entry, with its check, before writing the code.
   **Stop if:** you are about to make up a home for a technical kind of code.
3. **Reach for a pattern only when a real problem calls for it.** The catalogue, with use-when and not-when, is in [references/design-patterns.md](references/design-patterns.md). Prefer the language feature to ceremony: closed types with exhaustive matching beat a visitor, and a plain function beats a one-method interface.
4. **Run the checklist.**
   - [ ] Each changed unit keeps to one job in its layer, and no edge holds a rule, query or transaction.
   - [ ] Domain code clears the concept test.
   - [ ] A new interface marks a real boundary.
   - [ ] Each technical kind of code is in its place from step 2.
   - [ ] Any shared folder states its purpose, lists what may enter, and has an import test.
   - [ ] Expected failures are values. Every catch recovers visibly or rethrows.
   - [ ] Nothing is copied: constants, tokens, strings, contracts and rules each have one source.
   - [ ] Nothing calls out from inside a loop, lists have bounds, hot paths carry measurements.
   - [ ] Refactors and behaviour changes are separate.
   - [ ] Architecture tests pass with empty baselines, and any new structural rule shipped with its test.
   - [ ] If a problem got through, you can name the earliest rung of the `test-rules` ladder that should have caught it.
5. **Know when a plan review is due.** Each feature and each non-trivial fix gets a `plan-review` before the branch holds production code: at spec level on the epic, at slice level on each slice, at fix level on the bug. Trivial means one file, and no new type, file, dependency or rule. Anything larger is non-trivial. Hurry is no excuse to skip it.

## Done when
- [ ] The answer names the layer or entry, and the principle behind it.
- [ ] Any clash between a project rule and a principle is reported.
- [ ] A missing entry is proposed together with its check.

## Never
- Relax a project's rules on safety, privacy or testing.
- Cite precedent as the reason ("the old file does it"). Change the convention and its test.
- Invent paths, commands or APIs. Read them from the code.

## Next
- **Comes from:** `plan-review`, `build` (ship); `review-code` (check); `server-rules`, `app-rules`, `web-rules`
- **Leads to:** `decision` (kit) for a choice that is costly to reverse; `new-repo` (ship) to install the table and tests
