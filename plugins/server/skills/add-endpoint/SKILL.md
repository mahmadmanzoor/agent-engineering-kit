---
name: add-endpoint
description: "Add or change an API endpoint, contract first, on any stack. Edit the contract entry, write failing tests (forbidden callers included), build a thin handler over one use case, regenerate clients, and keep a drift test on the contract. Use when a route, request, response or error is new or changes. Say: '/server:add-endpoint', 'new endpoint', 'add a route', 'add an API for', 'expose this over HTTP', 'change the API'."
argument-hint: "[what the endpoint does, and who calls it]"
license: MIT
metadata:
  version: "1.0.0"
  model: sonnet
  effort: high
---

# Add endpoint

Build or change the endpoint described by `$ARGUMENTS`. No argument? Ask what it does and who may call it.

**Run on:** sonnet at high. The scope is clear, but a slip in access or compatibility costs a lot.

## Use it when
- You add or change a route, a request, a response or an error.

**Not for:** schema changes (`server:add-migration`), file transfer (`server:add-upload`), timed work (`server:add-job`).

## Before you start
Read `AGENTS.md` and `CLAUDE.md`. Gather:
- the contract file, and the command that generates clients;
- the error-code catalogue;
- the access rule for tenant-owned resources;
- the test host, plus one similar endpoint and its tests (copy the shape, not the flaws).

Do released clients (apps, partners) still call this API? If yes, each change must stay compatible (`ship:deploy-check`). Read `server:server-rules` for where handlers and services sit. Missing a fact? Ask once and offer to record it in `AGENTS.md`.

## Steps
1. **Edit the contract first.** No code yet. Settle the path, method, operation id (a verb like `getBooking`), tags, the shapes of request and response, all error statuses, and the callers allowed in. Apply these rules.

   Shape of the URL and verbs:
   - Paths look like `/v1/<plural-noun>/{id}/<sub-resource>`, with kebab-case segments. Ids are opaque strings. An action that is not CRUD is a `POST` to a verb sub-path.
   - `GET` is safe. `PUT` replaces and is idempotent. `PATCH` changes only the fields sent. `DELETE` is idempotent and returns `204`. Create returns `201`, with a `Location` header when a `GET` for the new item exists.
   - Bodies are camel-case JSON, enums are strings, times are ISO-8601 UTC. Secrets and codes go in bodies only, never in a path or query, because logs keep those.

   Failure and access:
   - Errors use problem details (RFC 9457). Each expected failure has a stable code in the catalogue, and clients key on the code. Use 400 (naming the fields), 401, 403, 404, 409 and 429.
   - Every endpoint needs authentication unless the contract marks it public. Rate-limit anything guessable or costly.
   - A caller outside the owning tenant gets 404. A member without the role gets 403, or whatever the project says. The use case checks this on every request, with no cached decisions. Removing a member also revokes that member's sessions for the tenant.

   Reads:
   - Filters are explicit query parameters, each backed by an index. Unknown values give 400.
   - Any list that can grow uses cursor paging: `limit` (default 50, max 200) and `after`. The response carries `items` and a `next` cursor or null. Never change the shape of a released list. Adding paging means a new operation.

   Writes and change:
   - A record a client may create offline carries a client-made id, and that id is a permanent unique key. Replaying it, even weeks on, returns the first resource: no error, no duplicate row.
   - An online-only create that may be retried carries an `Idempotency-Key` header. The server stores it for a window and replays the response. A windowed key is wrong for data that may wait in an offline queue past the window.
   - Only additive changes are safe. Anything breaking becomes a new version of the resource. Flag the old operation as deprecated and keep it until no supported client still calls it.
   - Uploads and downloads follow `server:add-upload`.

   **Stop if:** any response, each error included, is missing from the contract diff.
2. **Write failing tests.** Use integration tests that go through the real entry point, the real database and the project's test host. Cover:
   - success: the status and the exact body;
   - validation: each bad input returns 400 and names the field;
   - access: no credentials gives 401, non-member 404, member without the role 403, removed member 404;
   - idempotency: sending the same create twice leaves one row and the same response, also after the key window for offline records;
   - revocation: if a member is removed between two requests, the second one gets 404, cached session or not;
   - paging: the limit, the cursor, and the last page with `next` null;
   - domain conflicts and limits return the right code.

   Run them. Confirm each fails on an assertion, not on setup (`check:test-first`).
   **Stop if:** any test is red for a setup reason. Fix the setup first.
3. **Implement.** Follow `server:server-rules`.
   - The handler binds input, checks its shape, passes the caller's id to one service method and maps the result. It holds no data access, transaction or business rule.
   - The service authorises through the access unit, calls the domain, runs one transaction and notifies after commit.
   - Business rules live in the domain, reusable queries in persistence, locks in the lock unit.
   - Inject the clock. Put timeouts on I/O. Keep personal data out of logs. Add a metric for each new failure mode on a safety-critical path (`ship:observe`).
   - A schema change goes through `server:add-migration`.
4. **Regenerate clients.** Run the project's generator once per client of the contract. Generated code is never edited by hand. Run each client's analyze and test commands. Only the data layer may use a generated client.
5. **Verify.** Run the whole test suite for the area, then build with warnings treated as errors. If there is no contract drift test, add one. It diffs the contract the server emits against the contract file (operation ids, status codes) and fails when they disagree. For endpoints that touch personal data, sharing, auth or payments, run `check:security-review`.

## Done when
- [ ] The contract diff shows the endpoint and every error.
- [ ] Forbidden-caller tests exist and pass, with the output shown.
- [ ] The test suite, the build and the drift test pass, with commands and output shown.
- [ ] The PR carries the contract diff, the access tests and a statement on compatibility.

## Never
- Never ship a handler before its contract entry and before tests for forbidden callers.
- Never alter a released response shape in place. Add a version.
- Never place secrets, codes or personal data in a URL path or query string.
- Never hand-edit generated clients.

## Next
- **Comes from:** `build`, `feature` (ship)
- **Leads to:** `add-migration`, `add-upload`, `add-job` (server); `check:security-review`; `ship:deploy-check`
