# Python: Django and Django REST Framework

This page maps the server layers onto Django. Business rules go on models or in plain domain modules. Use cases go in services. Fat models are fine until they pick up technical code.

## Where things go
One Django app per feature area.

- **Domain:** `<area>/domain.py`. Plain classes, dataclasses, pure functions and constants. No `django.*` imports. If the project chose it, simple invariants may live on model methods.
- **Persistence:** `models.py` holds the mapping. `queries.py` holds reusable `QuerySet` methods or managers. Migrations live in `migrations/`.
- **Application:** `services.py`, one function or method per use case. Ports are Protocols in `<project>/ports.py`.
- **Edge:** `views.py` or `viewsets.py`, `serializers.py` for shapes and shape validation, and `urls.py`.
- **Access unit:** `access.py` with one function per resource kind, such as `require_member(user_id, workspace_id)`. Permission classes only call it.
- **Adapters:** `<project>/adapters/<vendor>.py`.
- **Workers:** `tasks.py`. Keep each task thin and have it call a service.

## Working rules
- **Views:** a view validates input, passes `request.user.id` to a single service, and maps what comes back. It never touches `Model.objects`. An import-linter contract can enforce that.
- **Serializers:** use plain `Serializer` classes for shapes. `ModelSerializer.save()` and generic views with `queryset=` push writes to the edge. If the project allows a read-only `ModelSerializer`, write that down and allowlist it.
- **Access:** the service calls the access unit. `has_object_permission` may hand off to it, but it must not hold a second copy of the rule. Results are never cached from one request to the next.
- **Errors:** define a small `Result` and `Error` type in services. One `EXCEPTION_HANDLER` renders the problem details. Call `get_object_or_404` only inside the access unit.
- **Reads:** `.only()`, `.values()`, annotations, `select_related`, `prefetch_related`, `.exists()`, and `.iterator()` for big scans.
- **Bulk writes:** `bulk_create`, `bulk_update`, and `QuerySet.update()`. The last one skips `save()` and signals.
- **Transactions:** open `transaction.atomic()` in the service. Lock rows with `select_for_update()`, guard invariants with `pg_advisory_xact_lock`, and run post-commit work in `transaction.on_commit(...)`. Leave `ATOMIC_REQUESTS` off, because it hides where the transaction starts.
- **Time:** pass a clock in. Do not call `timezone.now()` inside rules. Set `USE_TZ = True`.
- **Settings:** typed settings (pydantic-settings or django-environ), validated at import. `os.environ` appears only in settings.
- **Signals:** keep them out of business flow. Call the code directly.
- **Logging:** `logger.info("Booking %s confirmed", booking_id)`. Never an f-string that carries personal data.
- **Outbound calls:** `httpx` with explicit timeouts. Use `tenacity` for idempotent reads only. Only the task retries a send.
- **Sync by default:** keep request work short and queue the long work. Async views must use the async ORM methods and must never call blocking I/O.

## Tasks (Celery; RQ and django-q work alike)
- Enqueue after the commit: `transaction.on_commit(lambda: send_reminder.delay(item_id))`.
- Run one beat process per environment, rolling deploys included.
- `acks_late` plus a short visibility timeout can run a task twice, so make every task idempotent.
- Claim rows with `select_for_update(skip_locked=True).filter(...)[:100]` inside `atomic()`.
- For the sent-ledger, use `UniqueConstraint(fields=[...], name=...)`. Insert first. An `IntegrityError` means it was already sent.
- Check membership again when the task runs.

## Contract-first
Generate the schema with drf-spectacular (`manage.py spectacular --file <out> --validate`) and diff it against the contract file in a test or a CI step. Mark views with `@extend_schema` so operation ids and errors match.

## Testing and tooling
- **Database:** pytest-django with `@pytest.mark.django_db`. Use the real database, not SQLite, when production differs.
- **Query counts:** `django_assert_num_queries(n)`.
- **Architecture:** import-linter contracts, and a pytest that walks `ast` imports to check the domain allowlist.
- **Models:** a model is both mapping and entity. Choose once: rules on model methods, or plain domain classes mapped from models.
- **Migrations:** run `makemigrations`, read the SQL with `sqlmigrate <app> <n>`, use `AddIndexConcurrently` with `atomic = False`, and backfill in a task, not in the migration.
- **Full check:** `ruff format --check . && ruff check . && mypy . && pytest`. For mypy, install `django-stubs` and `djangorestframework-stubs`.
- **On-commit hooks in tests:** `TestCase` never commits, so `on_commit` callbacks stay silent. Use `captureOnCommitCallbacks(execute=True)` or its fixture. Without it a notification test passes while testing nothing.
- **Email:** the locmem backend and `django.core.mail.outbox`.

## Self-check greps
Each should return nothing for new code.

```bash
# ORM calls inside views
grep -rnE 'objects\.' --include='views.py' --include='viewsets.py' .
# clock reads inside rules and services
grep -rnE 'timezone\.now\(\)|datetime\.now\(\)' --include='domain.py' --include='services.py' .
# catch-all handlers
grep -rn 'except Exception' --include='*.py' .
# environment reads outside settings
grep -rn 'os\.environ' --include='*.py' . | grep -v settings
```
