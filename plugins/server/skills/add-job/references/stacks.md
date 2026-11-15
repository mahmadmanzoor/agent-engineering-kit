# Job tooling, stack by stack

Every section covers the same four points: the tools, keeping to one scheduler, claiming rows, and traps.

## Python with Django
- **Tools:** Celery workers plus exactly one `celery beat` (or `django-celery-beat`); RQ with rq-scheduler; django-q.
- **One scheduler:** keep a single beat replica. During a rolling deploy, shut the old beat down before the new one starts, or hold a scheduler lock.
- **Claiming:** call `select_for_update(skip_locked=True)` within `transaction.atomic()`.
- **Traps:**
  - If `acks_late` is on and the visibility timeout is shorter than the task, the task runs twice.
  - Enqueue through `transaction.on_commit`.
  - A `TestCase` only runs those callbacks inside `captureOnCommitCallbacks(execute=True)`.

## Spring (Java or Kotlin)
- **Tools:** `@Scheduled` with ShedLock; Quartz clustered over a JDBC store; or a queue consumer (SQS, RabbitMQ).
- **One scheduler:** one ShedLock lock per job name, or Quartz in cluster mode.
- **Claiming:** run `SELECT ... FOR UPDATE SKIP LOCKED` as a JPA native query or in jOOQ.
- **Traps:**
  - A method calling another method on the same class bypasses `@Transactional`.
  - `AFTER_COMMIT` events are lost when the process crashes, so use an outbox table.

## Node
- **Tools:** BullMQ repeatable jobs on Redis; pg-boss on Postgres; Agenda.
- **One scheduler:** BullMQ dedupes repeatable jobs by their key, and pg-boss `schedule` is a singleton.
- **Claiming:** pg-boss relies on `SKIP LOCKED`, while BullMQ pins each job to one worker with a lock.
- **Traps:** a rejected promise nobody handles kills the worker silently. Await every call and catch errors where the job starts.

## .NET
- **Tools:** Hangfire recurring jobs; Quartz.NET in a cluster; a `BackgroundService` driven by `PeriodicTimer` for simple loops.
- **One scheduler:** Hangfire's distributed lock per recurring job, or Quartz clustering.
- **Claiming:** use raw SQL with `FOR UPDATE SKIP LOCKED`, or `ExecuteUpdate` against a lease column.
- **Traps:** Hangfire retries 10 times by default. Set the attempts yourself so the job remains the one retry owner.

## Platform cron (Kubernetes CronJob, cloud schedulers)
- **Tools:** the platform hits an endpoint or launches a container on a timer.
- **One scheduler:** on Kubernetes set `concurrencyPolicy: Forbid`; elsewhere use the platform's single-run setting.
- **Claiming:** reuse the database claim shown in the sections above.
- **Traps:** outages cause missed runs. Set `startingDeadlineSeconds` and add a catch-up query that picks up overdue rows.

## The sent-ledger
Every stack uses the same table. Insert the row first. If the unique key is violated, the item was handled already: skip it.

```sql
CREATE TABLE reminder_ledger (
  booking_id  uuid NOT NULL,
  due_at      timestamptz NOT NULL,
  kind        varchar(40) NOT NULL,
  outcome     text,
  handled_at  timestamptz,
  UNIQUE (booking_id, kind, due_at)
);
```
