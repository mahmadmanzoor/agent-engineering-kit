# Architecture tests: allowlists that start empty

## Why an allowlist beats a denylist

Teams usually begin with a denylist test: "domain code must not touch the ORM". That test only stops what someone thought to name. A homemade image parser, a crypto helper and a JSON reader all slip past "no ORM in the domain", and the suite stays green while the design rots.

An allowlist flips it. "Domain code may use core language types, collections, text, and other domain code, and nothing else." A new dependency fails the test until a person widens the list, in review, and writes down why.

## Rules worth testing

1. **Domain allowlist.** Each domain type depends only on core language types, collections, text and regex, date and time types (but not clock reads), and other domain code.
2. **No raw bytes in the domain.** Domain signatures carry no byte arrays, streams or buffers.
3. **Edges stay away from data.** No entry-point module may name the persistence module, the ORM or the database driver. Health checks are the one allowlisted exception.
4. **One home per technical kind.**
   - Crypto APIs: only inside the named secret owners.
   - Storage SDKs: only in the storage adapter folder.
   - Limiter types: only in the limiter folder.
   - Field-error maps are built only in validation units.
   - Wire-name conversion happens in its one mapping.
5. **Generated code stays in the data layer.** Only the data or adapter layer may import generated client or bridge types.
6. **Shared code never imports a feature.** Nothing under `shared/` imports from `features/` (use the project's own folder names).
7. **Features meet through a public handle.** A feature reaches another one only through its domain or a single re-export file. No cycles.
8. **No direct clock or config reads.** Only the composition root may call clock APIs or read raw configuration.
9. **Size limits.** A file has at most N lines and M top-level types, in the layers where that matters.
10. **Allowlist entries must be real.** An entry that names a type which no longer exists fails the test.

## Baselines

- Start empty. A new rule arrives together with the code it forces to change.
- If one change cannot fix everything, keep a baseline file of the current offenders, one line of reason each. Add a second test that fails if an entry stops offending and is still listed, so the file can only shrink. Open an issue to empty it.
- Never allow an exception because one already exists. A present offender is no excuse for another.

## Tooling by stack

- **.NET:** ArchUnitNET or NetArchTest, run over the built assemblies.
- **Java and Kotlin:** ArchUnit. Add Konsist for Kotlin.
- **Python:** import-linter (layers, forbidden and independence contracts), or a pytest that walks the `ast` imports.
- **Node and TypeScript:** dependency-cruiser (`forbidden` and `allowed` rules), eslint `no-restricted-imports`, or the `boundaries` plugin.
- **Dart and Flutter:** a plain test that scans `lib/` and compares every `import` line with an allowlist.
- **Swift:** a script over the `import` lines of each target, or SwiftLint custom rules.
- **Go:** checks built on `go list -deps`, or depguard inside golangci-lint.
- **Anything else:** a short script over import statements. It is simple, and it is enough.

Keep the test in the regular suite, and have CI run it on each change. CI runs lint and formatting as well. That leaves reviewers free to look at what no machine can see.
