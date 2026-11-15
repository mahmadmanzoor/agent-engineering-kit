---
name: db-check
description: "Answer questions about data without risking it. Every call runs read-only under a statement timeout, work stays local unless the user okays a shared database, and shared ones use a read-only role. Covers schema, row counts, integrity, tenant isolation, freshness, query plans, and migration or backfill checks against a cohort and control rows. No personal data is shown. Say: '/server:db-check', 'query the database', 'check the data', 'explain this query', 'verify the migration', 'is the data correct'."
argument-hint: "[a data question, a migration to check, or a data bug you suspect]"
license: MIT
metadata:
  version: "1.0.0"
  model: sonnet
  effort: medium
---

# DB check

Use the database to answer `$ARGUMENTS`. Default to the local environment. With no argument, ask for the question or the migration to check.

**Run on:** sonnet at medium. The work is read-only and narrow. The rules below keep it safe.

## Use it when
- You need an answer about data, want to verify a migration or backfill, or are chasing a data bug.

**Not for:** repairing data. A repair is its own reviewed change. If you find a bug here, hand it to `ship:debug` or `ship:file-bug`.

## Before you start
Read `AGENTS.md` and the conventions for three things: how the local database starts, its connection settings, and the rules for shared environments (which people may connect, and through what path). Then read the real schema from the information schema, a describe command or the migrations. Table names below are examples.

**Stop if:** you do not know the environment, the access path or the real table names.

## Steps
1. **Choose the environment.**
   - **Local** (the project's compose file, a container, or a local install): read freely. Ask before writing seed or test data, and touch only rows you created yourself.
   - **Staging, production or any shared database:** only with the user's explicit OK for this session, through a read-only role on the approved path. Read only. No writes, no DDL, and no long scans at peak hours.
2. **Open every session read-only.** Set read-only mode and a statement timeout (say 30 seconds) on each call, since each new connection starts with default settings. To keep one session, put several queries in one script file. Put `LIMIT` on every exploratory query. Reach for `count(*)` and aggregates before row dumps. Outside local, never run an update, delete, DDL or lock-taking statement. Locally, only on your own test rows.
3. **Keep personal data out of sight.** Never print names, emails, phones, addresses, coordinates, tokens, free text or payment details in the chat, an issue, a PR, or any file. Aggregate them, bucket them (coordinates to about 10 km, times to the hour), or compare them inside the database. Refer to rows by id. Personal results stay out of git and the tracker.
4. **Run the checks you need.** Swap in the real names.

   ```sql
   -- Largest tables (this form is engine-specific; use your engine's equivalent)
   SELECT relname AS tbl, n_live_tup AS approx_rows FROM pg_stat_user_tables
   ORDER BY approx_rows DESC LIMIT 10;
   -- Last migrations applied
   SELECT * FROM <migration_history_table> ORDER BY 1 DESC LIMIT 3;
   -- Freshness: users with no note edited recently (count only)
   SELECT count(*) FROM users u
   WHERE NOT EXISTS (SELECT 1 FROM notes n WHERE n.author_id = u.id
                     AND n.updated_at > now() - interval '15 minutes');
   -- Gaps: notes per hour for one synthetic test user
   SELECT date_trunc('hour', updated_at) AS h, count(*) FROM notes
   WHERE author_id = '<test-id>' AND updated_at > now() - interval '1 day'
   GROUP BY h ORDER BY h;
   -- Integrity: orphans and impossible values
   SELECT count(*) FROM notes WHERE notebook_id NOT IN (SELECT id FROM notebooks);
   SELECT count(*) FROM booking_items WHERE seats < 1;
   -- Isolation: child and parent disagree on tenant
   SELECT count(*) FROM booking_items i
   JOIN bookings b ON i.booking_id = b.id
   WHERE i.tenant_id IS DISTINCT FROM b.tenant_id;
   -- Plan
   EXPLAIN (ANALYZE, BUFFERS) <query>;
   ```

   Before you judge a plan, seed synthetic data at 10 times today's volume. A plan over ten rows proves nothing.
5. **Verify a migration or backfill.**
   1. Before: count the rows expected to change (the cohort), and choose control rows that must stay as they are.
   2. Run the migration or backfill locally.
   3. After: the changed count equals the cohort, controls are untouched, no `NULL` sits where code now needs a value, constraints and indexes exist, and `EXPLAIN` shows the new indexes in use.

   **Stop if:** only the count matches. Check the cohort and the controls as well.
6. **Report.** List the question, the environment, the queries run (without personal results), the numbers, and your reading of them. Keep the facts separate from the reading.

## Done when
- [ ] Every session was read-only with a timeout (on shared environments, with the user's OK).
- [ ] The report lists queries and numbers and contains no personal data.
- [ ] For migrations, the checks show the cohort matched and controls did not change.

## Never
- Never write anywhere but local.
- Never touch a shared environment without an explicit OK for this session.
- Never put personal data in output that leaves the session.
- Never fix data in the middle of an investigation.

## Next
- **Comes from:** `add-migration` (server); `debug`, `incident` (ship); `perf-check`, `analytics-event` (check)
- **Leads to:** `ship:file-bug`, `ship:fix-bug` for a data bug
