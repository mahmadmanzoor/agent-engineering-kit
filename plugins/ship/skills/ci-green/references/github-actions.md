# Workflow file for GitHub Actions

Goals of this workflow:

- Hosted runners only, so a public repo stays safe.
- Path filters: a job runs only if its own area changed.
- A new push to a PR cancels the older run. Runs on `main` always finish.
- Every PR must point at an issue.
- Read-only token unless a job asks for more.

Rename the jobs for your project, then leave the names alone. Branch protection looks them up by name. The example is a notes app with `api/`, `site/` and `app/` folders.

## 1. Triggers, permissions, cancelling

```yaml
name: CI
on:
  push: { branches: [main] }
  pull_request:
permissions: { contents: read }
concurrency:
  # One group per PR branch. Pushes to main get a unique group, so nothing cancels them.
  group: ci-${{ github.event_name != 'pull_request' && github.run_id || github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}
```

## 2. Work out what changed

Every build job `needs` this one. A change to the workflow files lights up all areas.

```yaml
jobs:
  scope:
    name: What changed
    runs-on: ubuntu-latest
    outputs:
      api:  ${{ steps.paths.outputs.api }}
      site: ${{ steps.paths.outputs.site }}
      app:  ${{ steps.paths.outputs.app }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: paths
        with:
          filters: |
            api:  ['api/**', 'contracts/**', '.github/workflows/**']
            site: ['site/**', '.github/workflows/**']
            app:  ['app/**', 'contracts/**', '.github/workflows/**']
```

## 3. Require an issue link

```yaml
  linked-issue:
    name: PR links an issue
    if: ${{ github.event_name == 'pull_request' }}
    runs-on: ubuntu-latest
    steps:
      - name: Check the description
        env:
          AUTHOR: ${{ github.event.pull_request.user.login }}
          BODY: ${{ github.event.pull_request.body }}
        run: |
          # dependency bots never link issues
          [[ "$AUTHOR" == dependabot* || "$AUTHOR" == renovate* ]] && exit 0
          pat='(close[sd]?|fix(e[sd])?|resolve[sd]?) +#[0-9]+'
          grep -qiE "$pat" <<< "$BODY" || { echo "Add 'Closes #<issue>' to the description."; exit 1; }
```

## 4. Build jobs

Each calls one `make` target. The same target is what AGENTS.md tells people to run on their laptop.

```yaml
  api:
    name: API
    needs: scope
    if: ${{ needs.scope.outputs.api == 'true' }}
    runs-on: ubuntu-latest
    services:
      db:                         # service containers work on hosted Linux
        image: postgres:17
        env:
          POSTGRES_PASSWORD: test
        ports: ['5432:5432']
        options: --health-cmd pg_isready --health-interval 5s --health-retries 10
    steps:
      - uses: actions/checkout@v4
      # your language's official setup action goes in this slot; cache on the lock file
      - run: make api-check

  site:
    name: Site
    needs: scope
    if: ${{ needs.scope.outputs.site == 'true' }}
    runs-on: ubuntu-latest
    steps: [{ uses: actions/checkout@v4 }, { run: make site-check }]

  app:
    name: App (analyse + unit tests)
    needs: scope
    if: ${{ needs.scope.outputs.app == 'true' }}
    runs-on: ubuntu-latest        # Android and most cross-platform tests are fine on Linux
    steps: [{ uses: actions/checkout@v4 }, { run: make app-check }]

  ios-build:
    name: iOS build
    needs: scope
    if: ${{ needs.scope.outputs.app == 'true' }}
    runs-on: macos-latest         # iOS needs macOS. Those minutes cost more, so keep the job short.
    steps: [{ uses: actions/checkout@v4 }, { run: make ios-build }]   # PRs never sign
```

## Setting up each toolchain

Whatever the stack, pin the version your project actually uses.

- **Python.** `actions/setup-python`, with `python-version` and `cache: pip`. Or install uv or poetry. Cache on the lock file.
- **Node.** `actions/setup-node`, with `node-version` and `cache: npm` (or `pnpm`). Cache on the lock file.
- **Java and Kotlin.** `actions/setup-java` with `distribution: temurin`, plus `gradle/actions/setup-gradle`. Cache on the Gradle files.
- **.NET.** `actions/setup-dotnet`, with `dotnet-version` and `cache: true`. Needs a lock file, `packages.lock.json`.
- **Flutter.** `subosito/flutter-action`, with a pinned version, `cache: true`, keyed on `pubspec.lock`.
- **iOS.** Xcode ships on `macos-*` runners. Select a version with `sudo xcode-select -s`. Cache on `Podfile.lock` or package resolution.

Use the current major version of each action (read its README). A bot such as Dependabot or Renovate can bump the pins for you.

## Rules of thumb

1. **One command, two places.** Keep steps in a `Makefile` or script that CI and laptops both call. `ci-green` can then reproduce a failure exactly.
2. **Skipped is not always green.** It counts as passing only when that area did not change. Touching a workflow file runs everything.
3. **Pin actions.** A major tag is the least you do. Actions that see secrets or can write get a full commit SHA.
4. **Forks.** Runs triggered by a fork's `pull_request` get no secrets and a read-only token. That is the safe default. Do not use `pull_request_target` together with a checkout of the PR head.
5. **Self-hosted runners:** private repos only. A public repo lets any fork PR execute code on that box.
6. **Required checks** go in branch protection or rulesets, by job name. While PR CI is switched off, merging is gated by running the same commands on your machine against the head commit. Paste their summary into the PR.
7. **Cheap jobs on every PR.** Link check, lint and docs catch most review comments before a person opens the diff.
