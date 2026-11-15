# The workflow

One skill per step. Each skill reads the project's own rules first. If a step has a skill, use it instead of improvising.

## The path a feature takes

```
idea ─► ship:idea-brief ─► ship:new-repo
                           (repo, protected main, tracker, AGENTS.md, walking skeleton,
                            placement table + architecture tests, CI)

feature ─► ship:feature-research ─► ship:write-spec ─► ship:plan-review (spec level)
           ─► ship:spec-to-issues (epic + slices)
   small ─► ship:feature-research ─► ship:file-issue
bug     ─► ship:file-bug ─► ship:debug (reproduction test) ─► ship:fix-bug

ship:start-issue ─► ship:plan-review (slice level, BEFORE production code)

ship:build
  ├─ rules:   ship:code-placement, server:server-rules, web:web-rules, mobile:app-rules, mobile:shared-core
  ├─ tests:   check:test-rules, check:test-first, check:write-tests
  ├─ parts:   server:add-endpoint, server:add-migration, server:add-job, server:add-upload,
  │           web:build-screen, web:add-page, mobile:design-to-screen,
  │           mobile:background-work, mobile:offline-queue, mobile:home-widget, check:analytics-event
  └─ checks:  check:perf-check, check:a11y-audit, check:security-review (when touched)

ship:commit-check ─► ship:open-pr ─► check:review-code (crew:code-reviewer posts it)
ship:ci-green ─► ship:deploy-check ─► mobile:device-test (mobile changes)
ship:merge-gates ─► ship:release ─► ship:observe ─► ship:cleanup

when it breaks: ship:incident ─► ship:postmortem ─► kit:lesson ─► kit:new-skill
```

## Solo shortcut

Alone on a small, low-risk change? Skip the spec, epic and issues: "just build it". Keep these anyway:

- `ship:plan-review` when the change touches data, money, auth or anything a user relies on.
- `check:test-first` for the failure paths of that same code.
- `ship:commit-check` (the `guard` hooks cover part of it).

## Which skill when

| You want to | Skill |
|---|---|
| Turn an idea into a brief and MVP | `ship:idea-brief` |
| Make a repo agent-ready | `ship:new-repo` |
| Build one feature end to end | `ship:feature` |
| Understand a feature first | `ship:feature-research` |
| Write the plan for a big feature | `ship:write-spec` |
| Split a spec into issues | `ship:spec-to-issues` |
| File one feature slice or a bug | `ship:file-issue`, `ship:file-bug` |
| Pick up an issue | `ship:start-issue` |
| Review a plan before code | `ship:plan-review` with `crew:plan-reviewer` |
| Build an approved change | `ship:build` |
| Find and fix a bug | `ship:debug`, `ship:fix-bug` |
| Decide where code goes | `ship:code-placement` |
| Commit, open a PR, get CI green | `ship:commit-check`, `ship:open-pr`, `ship:ci-green` |
| Check what breaks after deploy | `ship:deploy-check` |
| Merge, release, watch production | `ship:merge-gates`, `ship:release`, `ship:observe` |
| Handle an outage and write it up | `ship:incident`, `ship:postmortem` |
| Tidy up after merge | `ship:cleanup` |
| Test rules, test-first, write tests | `check:test-rules`, `check:test-first`, `check:write-tests` |
| Review code | `check:review-code` with `crew:code-reviewer` |
| Security, accessibility, performance | `check:security-review`, `check:a11y-audit`, `check:perf-check` |
| Add a product event | `check:analytics-event` |
| Server structure, endpoint, migration, job, upload, DB question | `server:server-rules`, `server:add-endpoint`, `server:add-migration`, `server:add-job`, `server:add-upload`, `server:db-check` |
| Web structure, app screen, content page | `web:web-rules`, `web:build-screen`, `web:add-page` |
| Mobile structure and parts | `mobile:app-rules`, `mobile:shared-core`, `mobile:background-work`, `mobile:offline-queue`, `mobile:design-to-screen`, `mobile:home-widget`, `mobile:device-test` |
| Write a skill, record a lesson or decision | `kit:new-skill`, `kit:lesson`, `kit:decision` |

## Models

Each skill names its model and effort. Rough rule: Opus for anything where a wrong call is expensive (plan and code review, security, migrations, debugging, incidents), Sonnet for scoped building and drafting, Haiku for tidy-up and lookups. Subagents should always be given a model on purpose.
