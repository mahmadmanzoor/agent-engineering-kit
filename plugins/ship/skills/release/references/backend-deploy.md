# Deploying a backend

## The order that keeps data safe

1. **Expand the schema.** Ship additive migrations first: nullable columns, new tables, concurrent index builds. Old code must still run on the new schema.
2. **Release the new code.** Any migration still in progress means the code writes both shapes.
3. **Backfill in batches.** Use a separate batched job. Do not put the backfill in the migration.
4. **Contract the schema.** A later deploy, on its own, drops old columns or sets new ones as required. Only do it when nothing running, and no client you still support, reads the old shape.

If a migration is not additive, it cannot go out ahead of the code that depends on it. Give it its own contract deploy.

## Picking a rollout style

- **Rolling.** Instances are swapped a few at a time. Good for stateless services. For a while both versions answer requests, so each must work with the schema and the contract as they stand.
- **Blue/green.** The new version starts beside the old, then traffic flips in one move. You can undo it just as fast. Both colours share the database, so a migration must be safe for both.
- **Canary.** A small slice of traffic reaches the new version. You compare signals and widen the slice. This suits risky changes. It depends on metrics split per version, and sticky sessions may hide problems.
- **Feature flag.** The code ships switched off and is enabled for chosen groups. Use it for behaviour changes and safety-critical paths. A flag without an owner and an exit condition becomes clutter.

## Jobs and workers while a deploy runs

1. **Run one scheduler.** Under a rolling or blue/green deploy two versions overlap. If each of them starts the scheduler, every scheduled job fires twice, which means duplicate reminders and double charges. Give the scheduler a process of its own with a single instance, or guard it with a lock or leader election that both versions obey.
2. **Let workers drain.** At shutdown a worker accepts no new jobs. Within a grace period it finishes the current job or hands it back. Redelivery happens after a visibility timeout or a late ack, so every job has to be idempotent, for example with a unique sent-ledger key (see `add-job`, server plugin).
3. **Keep payloads compatible both ways.** Old code may queue a job that new code executes, and vice versa. Evolve job payloads additively, as with the API.
4. **Build a pause switch.** You need to freeze the scheduler, and turn off one job, with no deploy. A flag or an admin command will do. It is the first thing to reach for when messages go out twice.

## Smoke test right after the deploy

- Readiness endpoint reports the database reachable, migrations applied and caches reachable.
- One authenticated request succeeds along the real path.
- Per-route error rate and p95 latency match the pre-deploy baseline (`observe`).

## Going back

- Redeploy the earlier image or artifact. Never delete the last good one.
- Fix forward with a new migration rather than a down migration. Run a down migration only if you have tried it on a copy of production-like data.
- If the change is behind a flag, switching it off is the quickest way back.
