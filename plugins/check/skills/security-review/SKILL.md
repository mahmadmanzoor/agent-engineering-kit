---
name: security-review
description: "Check a change, spec or feature for ways it could leak personal data or be turned against its users. Trace every piece of personal data end to end, test who may call what (forbidden-caller tests), check consent, play abuse cases, hunt leaks into logs, errors, telemetry and analytics (owns the logging rule), and cover uploads, secrets, an API top-ten pass, retention and deletion. Use when work involves personal data, auth, sharing, money, uploads, exports or a new third-party SDK. Say: '/check:security-review', 'can this leak', 'is this safe', 'threat model this', 'privacy review', 'abuse case', 'security review'."
argument-hint: "[what to review: PR, branch, spec or feature]"
license: MIT
metadata:
  version: "1.0.0"
  model: opus
  effort: high
---

# Security review

`$ARGUMENTS` is a PR, branch, spec or feature. Find the ways it could expose a person's data or be abused. With no argument, review the current branch's diff.

**Run on:** opus at high. A leak harms a person and is hard to take back.

## Use it when
- The change involves personal data, sharing or visibility, roles and invites, sign-in and sessions, payments, notifications, analytics, uploads, exports, deletion, or adds a third-party SDK.
**Not for:** general review (`/check:review-code`). Speed (`/check:perf-check`).

## Before you start
Read AGENTS.md, CLAUDE.md, SECURITY.md and any privacy policy or data inventory. Note which data the project calls personal, its retention periods and its "access denied" status codes. Then read the diff or spec and trace everything it reaches: entry points, use cases, storage, calls out, logs. The project may have no written data rules. Then step 5 is your default, and you offer to write it into the project docs.

## Steps
1. **Map the data flow.** Take each piece of personal data the change touches (names, contact details, location, payment, health, photos, messages, device ids). Answer six questions about it: where is it created, where is it stored (table, cache key, device storage), where does it go (API, realtime channel, push, email or SMS, analytics, error reports, third parties), who can read it, how long is it kept. Put the answers in a table with one row per data item.
   **Stop if:** any answer is unknown and not logged as a finding. An unknown answer is the first finding.
2. **Authorisation and isolation.**
   - Every endpoint, realtime method and job verifies two things: the caller owns the resource or is a member, and holds the role the action requires.
   - Do not trust ids in URLs. A resource from another tenant returns the project's not-found status, which hides that it exists. Integration tests prove it for a non-member, for a member without the role, and for a removed member.
   - The server joins realtime groups from membership. It ignores any group name the client sends.
   - Losing access takes effect at once, caches too. That covers removal, a role change and a closed account. Test it.
   - Share links and invites need 128 or more random bits, an expiry, revocation, a narrow scope and a rate limit. Revocation is immediate.
3. **Consent and visibility.**
   - Sharing is opt-in. People can see who has access to what, and can end it.
   - No quiet collection: a new way of viewing someone's data appears on their own screen.
   - For people who cannot consent (children, dependants), record who consented and what the person is shown.
4. **Abuse cases.** Picture who might misuse the feature, then ask what each could do.

   | Who | Questions |
   |---|---|
   | Whoever finds a lost or stolen device | What can they read? Can the owner sign the device out remotely? |
   | Manager | Can data gathered for work (locations, timestamps, photos, activity) track someone beyond the task, such as off hours, at home or over time? Collect only what the task needs. Show the person what is recorded. Restrict who sees history. |
   | Support or admin staff | Can the tools show more than the task needs, without an audit trail? |
   | Ex-employee or removed member | Can they keep a link, token or cached data? |
   | Any viewer | Can history, exports, screenshots or notifications show more than the live view permits? |
   | Controlling partner or ex | Can they add a person or device to a group unnoticed? Can a privacy choice (hide, pause, block) be detected, punished or exposed? |
5. **Leaks: the logging rule.** This skill owns the rule.
   - **Rule:** personal data never appears in anything that leaves the device or the server process. Personal data here means: tokens and secrets, message text, health and payment data, addresses, precise location, contact details, names.
   - **Channels it covers:** release-build client logs, shipped server logs at every level, exception messages, URLs and query strings, error-report events and breadcrumbs, metrics, traces, analytics.
   - **Exceptions:** local debug builds with synthetic data. Opaque ids may appear in logs, never as metric tags (cardinality, re-identification).
   - **Objects count.** A log line, attribute or exception holding an object that carries personal data breaks the rule like the raw field does. Destructuring and default string conversion are included. Make those types print without the data.
   - **Check the diff.** Search the new log, print, telemetry and exception lines for personal fields. Read multi-line log calls whole, since a line search misses them.
   - **Notifications.** Keep sensitive content off the lock screen unless the person chose otherwise. Keep data payloads small.
   - **Analytics.** No personal data or free text (`/check:analytics-event`).
   - **Third parties.** No personal data to ad or analytics SDKs. A new SDK needs a decision record (`/kit:decision`, kit) and a privacy note.
6. **Security basics.**
   - **API top-ten pass.** Broken object-level authorisation. Broken authentication. Broken property-level authorisation (excess data, mass assignment). Unrestricted resource use. Broken function-level authorisation. Unrestricted sensitive flows. Server-side request forgery. Misconfiguration. Improper inventory. Unsafe use of third-party APIs.

   - **Transport.** HTTPS only.
   - **Dependencies.** A new package needs a reason, a maintained source and a licence check. None may send user data home.
   - **Metadata the product needs** (capture time, capture place as evidence). Never leave it inside the file. Extract just the fields you need into structured, consented data. Give it its own retention and access rule. Then strip the file.
   - **Uploads** (`/server:add-upload`, server). Enforce a size limit. Take the type from the bytes, not the name. Re-encode on the server. Strip metadata such as location and device serials on the device when possible, and again on the server before storing. Save outside the web root under a random name. Serve through a signed or authorised URL. Never execute the file or render it as HTML.
   - **Input.** Validate at the boundary. Cap upload and batch sizes. Never assemble a query by joining strings.
   - **Secrets.** One owner and one config entry per purpose, validated at start-up. Never fall back to another purpose's key. Never in the repo or client bundle.
   - **Data on the device.** Queues, caches and files holding personal data go in app-private storage, outside cloud backup where possible. Encrypt sensitive ones (platform file protection, or an encrypted database with its key in secure storage). Clear them on sign-out only if nothing unsent would be lost (`/mobile:offline-queue`).
   - **Web sessions.** Use a cookie with HttpOnly, Secure and SameSite. Never use local storage. Cookie sessions need CSRF protection on every state-changing request. Encode output by default, never render raw HTML taken from data, and set a content security policy without inline scripts.
   - **Mobile tokens.** Keep them in the platform's secure storage. Never in plain preferences or files.
   - **Sessions.** Short-lived access tokens plus refresh. Sign-out and account deletion revoke them. The server can revoke all sessions of one device or account.
   - **Sign-in.** Rate-limit one-time codes per identifier and per IP. Add attempt limits and expiry. Error text must not reveal whether a user exists.
7. **Retention and deletion.** Keep data for the period the project states, no longer. Deleting an account removes or anonymises every row that identifies the person, including analytics and media. Backups follow the same rule within their window.
8. **Write the review.**
   ```markdown
   ## Security review: <change>
   Risk rating: low, medium or high

   ### Data flow
   (the table)
   ### Findings
   - [critical|major|minor] the issue; the scenario (who is hurt, how); the fix; its proving test
   ### Abuse cases tried
   ### Checked, no issue
   ```
   **Stop if:** a finding has no proving test. Usually that is an integration test with a forbidden or removed caller.
   On a PR, post one comment headed `## Security review - <short head SHA>`, after checking it against the project's attribution rules. Ask first on someone else's PR. On a spec, add it to the spec's review notes.

## Done when
- [ ] The data-flow table is complete, or each gap is a finding.
- [ ] Steps 2 to 7 each end in findings or in "checked and fine".
- [ ] Each finding names the test that proves its fix.
- [ ] A risk rating exists, and the review is posted or handed over.

## Never
- Merge past a `critical` finding, unless the owner's acceptance is quoted in the PR (`/ship:merge-gates`, ship).
- Paste real personal data into a review, issue or PR. Invent examples.
- Decide that data is not personal on a hunch. When unsure, it is personal.

## Next
- **Comes from:** `/check:review-code` (dimension 2), `/ship:write-spec`, `/ship:plan-review` (ship), `crew:code-reviewer` (crew)
- **Leads to:** `/ship:file-bug` (ship) for findings outside the change. `/kit:decision` (kit) for a new SDK.
