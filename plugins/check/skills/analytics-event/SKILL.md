---
name: analytics-event
description: "Define a new product analytics event, change one, or turn a usage question into a query over event data, collecting no personal data. Question first, then object_action names, allow-listed properties, server-side hashed ids, consent respected, a catalogue as the single record, and tests for both the sent event and the opt-out. Cohort queries for questions. Use for any request to measure usage. Say: '/check:analytics-event', 'track this', 'new analytics event', 'measure adoption', 'who uses this', 'funnel for', 'retention'."
argument-hint: "[add <thing to measure> | a usage question]"
license: MIT
metadata:
  version: "1.0.0"
  model: sonnet
  effort: medium
---

# Analytics event

Two kinds of input: `add <thing to measure>`, or a plain question like "how many new notebooks got a first note in week 1?". No input: ask which kind. The only thing product analytics answers is whether people use a feature.

**Run on:** sonnet at medium. The rules are fixed and tests enforce them.

## Use it when
- Someone wants to measure usage, or has a question that event data can answer.
**Not for:** system health, errors and uptime (`/ship:observe`, ship).

## Before you start
Read AGENTS.md or CLAUDE.md and any analytics decision record. Learn whether the team runs the pipeline or a vendor does. Locate: the event catalogue (for example `docs/analytics/events.md`), the client API, the transport layer, the storage table, the consent setting.

No pipeline yet? Treat building it as separate work (`/ship:file-issue`, ship). It needs a catalogue, a typed client API (batching, opt-out), an ingest endpoint, a table and a chart source. Keep the whole path in your own stack: app, your API, your database, your charts. Before adding a vendor SDK, write a decision record (`/kit:decision`, kit) and get the user's call.

## Design rules

**Catalogue.** One record for everything. Row = event, properties, question answered, owner. No row, no sending.

**Client API.** Events are typed, like `analytics.track(NoteCreated(source: "share-sheet"))`. Feature code never hands over a free-form map.

**Transport.** Hold events in a local queue while offline. Send in batches. Discard any older than N days. Sending must not hold up the screen or anything safety-critical.

**Storage.** Columns: `time`, `name`, pseudonymous user id, pseudonymous tenant id, platform, app version, properties. Write down the retention period (for example 13 months). Deleting an account deletes that person's rows.

**Ids.** The server hashes: `HMAC-SHA256(server secret, id)`. One person's events still join to each other. Without the secret, nobody can link them to a user table. The secret gets its own config entry, used for this purpose only.

## Steps
**A. Add an event**
1. **Justify it.** State the product question. If you cannot, stop: no question means no event.
2. **Name it** `object_action`, snake_case, past tense. Examples: `note_created`, `booking_confirmed`, `checkout_abandoned`, `onboarding_step_completed`. A new property on an existing event beats a near-copy.
3. **Check each property against the allow-list.**

   | Allowed | Forbidden |
   |---|---|
   | Enums (`source: share-sheet\|button\|import`, `platform`) | Location, distances, addresses, place names |
   | Counts and durations in seconds | Contact details and names |
   | Booleans, app version, step names | Text of messages, notes or searches; photos |
   | | Device or network ids; raw user or tenant ids (hash in transport) |
   | | Tokens, health data, payment data |

   **Stop if:** a property fits neither column cleanly. Drop it.
4. **Honour consent.** Check the in-app analytics switch. When off, queue nothing. Every feature behaves the same either way.
5. **Write the catalogue row** alongside the code.
6. **Test two things.** With a fake sink: after the user action, the exact name and properties arrive. With analytics off: nothing arrives. Add a catalogue test that fails when typed events and catalogue rows disagree.
7. **Review new properties** with `/check:security-review`, step 5.
   **Stop if:** the question, the row or either test is missing. Do not ship.

**B. Answer a question**
1. Pin the question down: who is counted, over which window, using which events, and what "active" means here.
2. Look for the events in the catalogue. A cohort question needs a start event too. Where one is missing, add it first, and say the answer only covers the time since it shipped.
3. Run the query read-only (`/server:db-check`, server). Example: share of new notebooks with a first note inside 7 days.
   ```sql
   SELECT date_trunc('week', s.t) AS cohort_week,
          count(*) AS new_notebooks,
          count(n.notebook_hash) AS with_first_note
   FROM (SELECT notebook_hash, min(time) AS t FROM analytics_events
         WHERE name = 'notebook_created'
           AND time BETWEEN now() - interval '60 days' AND now() - interval '1 week'
         GROUP BY 1) s
   LEFT JOIN (SELECT DISTINCT notebook_hash, time FROM analytics_events
              WHERE name = 'note_created') n
     ON n.notebook_hash = s.notebook_hash AND n.time < s.t + interval '7 days'
   GROUP BY 1 ORDER BY 1;
   ```
4. Reply with the figures, then the definition, the window and the caveats: opt-outs, and app versions that never sent the event. Treat small samples with care.
5. A question that recurs deserves a saved chart. Link it from the catalogue row.

## Done when
- [ ] Event: the question, the row and both tests exist, and the tests pass (command and result line).
- [ ] Question: the reply gives the definition, window and caveats, and the query was read-only.

## Never
- Send personal data in any event. Doubt means leave it out.
- Let analytics delay a safety-critical path, even briefly.
- Add a third-party analytics SDK without a decision record and the user's decision.

## Next
- **Comes from:** `/ship:write-spec` (analytics section, ship), a product question
- **Leads to:** `/check:security-review` for new properties. `/server:db-check` (server) for queries. `/ship:observe` (ship) for system health.
