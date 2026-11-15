# Python testing notes

## Running tests
- One test: `pytest tests/test_notes.py::test_rejects_title_over_80_chars`, or select by keyword: `pytest -k "80_chars"`
- One folder: `pytest tests/notes`
- Everything: `pytest`
- After a change to time logic, run once as `TZ=Pacific/Auckland pytest`.

## Tools
- **Framework:** pytest. Django projects use pytest-django or the built-in runner, per the project.
- **Clock:** hand `now` or a clock object to the code. `time-machine` or `freezegun` belong at the edge only.
- **Parameterised tests:** `@pytest.mark.parametrize`.
- **Vendors:** recording fakes injected through settings or DI. For recorded HTTP use `responses` or `respx`.
- **Architecture rules:** import-linter contracts, or a small walker over the `ast`.
- **Test client:** Django's test client or `APIClient`, FastAPI's `TestClient`, Flask's `app.test_client()`.
- **Database:** the real engine, from a container or a local service. Use a transaction or a fresh schema per test (pytest-django's `db` fixture, with `--reuse-db` on a dev machine).
- **Query counts:** `django_assert_num_queries(n)`, or in SQLAlchemy an event listener on `before_cursor_execute`.

## Django traps
- **After-commit work.** `TestCase` wraps each test in a transaction that never commits. Any `transaction.on_commit` callback (sending mail, queueing a task) never runs, so a test can pass for the wrong reason. Wrap the call in `with self.captureOnCommitCallbacks(execute=True):`, use pytest-django's `django_capture_on_commit_callbacks`, or switch to `TransactionTestCase` when you need real commits.
- **Email.** The in-memory backend collects messages in `django.core.mail.outbox`. That makes it your recording sender. Assert recipient, subject and count. Include a rerun that must send nothing.

## Celery tasks
Call the task function directly, with fakes for vendors. Prove idempotency by calling it twice. Eager mode (`task_always_eager`) hides serialisation, retries, `acks_late` redelivery and commit timing. Keep it for wiring tests, and cover redelivery on purpose.

## Sample
```python
import pytest
from notes.domain import title_fits

@pytest.mark.parametrize("length, expected", [(80, True), (81, False)])
def test_title_allows_at_most_80_characters(length, expected):
    assert title_fits("a" * length) is expected
```
