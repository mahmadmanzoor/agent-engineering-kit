# Placement table template

Paste the template below into the project's conventions doc (for example `docs/conventions.md`, linked from AGENTS.md) and swap in real paths. Write one entry per technical kind of code. Every entry names the check that enforces it. Where no check exists, write "review", so readers know a person has to judge it.

The example is a shop with orders and notifications.

```markdown
## Home of each kind of code

### Entry points (HTTP, jobs, consumers, screens)
- Path: `src/<area>/api/`
- Rule: stay thin. Check the input shape, authenticate, give one use case the caller id, map what comes back.
- Check: `ArchTest.edges_never_touch_data`

### Use cases
- Path: `src/<area>/application/`
- Rule: one method per use case. Authorise through the access-check unit. Own the transaction.
- Check: review

### Business rules
- Path: `src/<area>/domain/`
- Rule: pass the concept test. Import only from the allowlist.
- Check: `ArchTest.domain_imports_allowlist`

### Input shape validation
- Path: `src/<area>/api/<area>_validation.*`
- Rule: the only code that builds a field-error map.
- Check: `ArchTest.field_errors_only_here`

### Secrets and crypto
- Path: `src/security/<purpose>/`
- Rule: each purpose has one owner and one config section, validated at start.
- Check: `ArchTest.crypto_has_owners`

### Object storage
- Path: `src/storage/`, with one port and one adapter per provider.
- Rule: no storage class per feature.
- Check: `ArchTest.storage_sdk_only_here`

### File formats and parsing
- Path: next to its port, in `src/storage/` or `src/<area>/adapters/`.
- Rule: never in the domain.
- Check: `ArchTest.domain_has_no_raw_bytes`

### Rate limiters
- Path: `src/rate_limiting/`
- Rule: say whether it fails open or fails closed.
- Check: `ArchTest.limiters_only_here`

### Background loops
- Path: `src/background/`
- Rule: each pass calls exactly one use case.
- Check: `ArchTest.loops_call_one_use_case`

### Scheduled jobs
- Path: `src/jobs/`, plus a single scheduler config.
- Rule: one scheduler instance. Idempotent. Claim work with leases. Unique sent-ledger. Re-check access at run time.
- Check: `ArchTest.jobs_call_one_use_case`, plus a race test

### Outbound notifications
- Path: `src/notifications/` with a port, one adapter per channel, and templates.
- Rule: honour user preferences. Unique ledger key. Re-check access at send time.
- Check: `ArchTest.notification_sdk_only_here`

### File uploads
- Path: `src/uploads/` (a single reader) and `src/storage/`.
- Rule: detect the type from the bytes, cap the size, strip metadata. The parent record is complete only after every file is confirmed.
- Check: `ArchTest.raw_body_read_in_upload_reader_only`

### Shared code
- Path: `src/shared/`
- Rule: Purpose: ... May contain: ... Never imports a feature.
- Check: `ArchTest.shared_never_imports_features`

### Wire contract
- Path: `contracts/api.yaml`, generated into `src/<client>/api/`.
- Rule: generated types stay in the data layer.
- Check: `ArchTest.generated_types_stay_in_data`

### Configuration
- Path: `src/<area>/<area>_options.*`
- Rule: validate at start. No raw lookups.
- Check: `ArchTest.no_raw_config_reads`

### Time
- Path: an injected clock.
- Rule: never read the system clock directly.
- Check: `ArchTest.no_direct_clock_reads`
```

## Filling it in

1. **Survey the code.** Run `ls` on the source tree. Grep for crypto, storage SDKs, HTTP clients, timers and loops, and look for folders named `utils`, `helpers` or `common`.
2. **Pick one home** for each kind that shows up in several places. Treat the move as its own refactor change that leaves behaviour alone.
3. **Check, then move.** Write the check and see it fail. Move the code and see it pass. If it cannot pass yet, let it keep a baseline that may only shrink. Give every entry a reason and open an issue to empty the baseline.
4. **Link the table from AGENTS.md** so each agent reads it before writing code.
