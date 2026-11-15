# agent-engineering-kit

My Claude Code setup, packaged so you can install it too.

It covers the work I do with coding agents every day: taking a feature from idea to production on backend, web and mobile, reviewing plans and code with agents that never saw the chat, and keeping secrets out of git. It also has the skills I use for LinkedIn, ChatGPT ads and short video reels.

Every skill is a plain `SKILL.md`, so it also works in Codex, Cursor, Gemini CLI and GitHub Copilot.

## How I use it

**Everything is off by default.** I turn plugins on per project, only when the work fits. A mobile skill has no business loading while I fix a marketing site. Every enabled skill adds its description to every session, so fewer skills means less noise and fewer wrong triggers.

**Every skill says what to run it on.** Each `SKILL.md` has `model` and `effort` in its frontmatter and a **Run on:** line. Reviews, debugging, migrations and incidents run on Opus. Writing tests, filing issues and drafting run on Sonnet. Tidy-up runs on Haiku. Raise effort one level before moving up a model.

**Solo or team, same rules where it matters.** The full flow (spec, issues, plan review, PR, merge gates) is built for shared repos. Working alone on a small change, say "just build it" and skip the paperwork. The plan review and test-first rules still apply when the code can hurt a user or lose data.

## Install

### Claude Code

```text
/plugin marketplace add mahmadmanzoor/agent-engineering-kit
/plugin install guard@agent-engineering-kit
```

Then install what you need and keep it off until a project needs it:

```bash
claude plugin install ship@agent-engineering-kit
claude plugin disable ship@agent-engineering-kit
```

Turn a plugin on for one project only, from inside that project:

```bash
claude plugin enable mobile@agent-engineering-kit --scope project
```

That writes `enabledPlugins` into the project's `.claude/settings.json`, so the whole team gets the same skills.

Skills are namespaced: `/ship:feature`, `/check:review-code`, `/server:add-migration`. Agents: `crew:plan-reviewer`, `crew:code-reviewer`, `crew:test-writer`.

### Other agents

```bash
git clone https://github.com/mahmadmanzoor/agent-engineering-kit
cd agent-engineering-kit
scripts/install-skills.sh ./.agents/skills                 # copy all skills
scripts/install-skills.sh ~/.codex/skills --link            # link, stays in sync
scripts/install-skills.sh .cursor/skills --only ship,check  # some plugins only
```

See [docs/other-agents.md](docs/other-agents.md) for using the review agents where there are no subagents.

## Start here

| You have | Run |
|---|---|
| An idea, no repo | `ship:idea-brief`, then `ship:new-repo`, then `ship:feature` |
| A repo with no agent rules | `ship:new-repo` (adds `AGENTS.md`, placement table, architecture tests, CI) |
| A feature to build | `ship:feature` (it chains the rest) |
| A bug | `ship:file-bug`, `ship:debug`, `ship:fix-bug` |
| Production is down | `ship:incident`, then `ship:postmortem`, then `kit:lesson` |

The full map: [docs/workflow.md](docs/workflow.md).

## What's inside

| Plugin | Turn on when | Skills |
|---|---|---|
| `guard` | Always | Hooks: block commits that add a secret, block commits on `main` |
| `ship` | Shared repos with issues and PRs, or any serious feature | `feature`, `idea-brief`, `new-repo`, `feature-research`, `write-spec`, `spec-to-issues`, `file-issue`, `file-bug`, `start-issue`, `plan-review`, `build`, `debug`, `fix-bug`, `commit-check`, `open-pr`, `ci-green`, `deploy-check`, `merge-gates`, `release`, `observe`, `incident`, `postmortem`, `cleanup`, `code-placement` |
| `check` | Tests, reviews, security, accessibility, performance | `test-rules`, `test-first`, `write-tests`, `review-code`, `security-review`, `a11y-audit`, `perf-check`, `analytics-event` |
| `crew` | With `ship` or `check` | Agents: `plan-reviewer`, `code-reviewer`, `test-writer` |
| `server` | A real server: database, migrations, jobs, uploads | `server-rules`, `add-endpoint`, `add-migration`, `add-job`, `add-upload`, `db-check` |
| `web` | Web apps and content sites | `web-rules`, `build-screen`, `add-page` |
| `mobile` | Phone apps on any stack | `app-rules`, `shared-core`, `background-work`, `offline-queue`, `design-to-screen`, `home-widget`, `device-test` |
| `kit` | Writing skills, ADRs, lessons | `new-skill`, `lesson`, `decision` |
| `linkedin` | Writing for LinkedIn | `li-post`, `li-human`, `li-comment`, `li-reply`, `li-dm`, `li-inbox`, `li-plan`, `li-audit`, `li-profile`, `li-carousel`, `li-repurpose` |
| `ads` | ChatGPT Ads Manager | `chatgpt-ads-campaign`, `chatgpt-ads-context-hints`, `chatgpt-ads-csv-upload` |
| `video` | Short vertical video ads | `reel-studio` |

`ship` needs `check` and `crew`. `server`, `web` and `mobile` need only `check`, so turning on `mobile` does not pull in the whole issue-and-PR flow.

## The ideas behind it

- **Review the plan before the code.** A fresh agent checks where each part goes, what already exists to reuse, and whether the next feature would have to write it again.
- **Review placement separately from bugs.** A wrong placement gets copied by the next feature, so it counts as a major finding.
- **One home for each kind of code.** Secrets, storage, uploads, background loops: each has a stated place and a test that keeps it there.
- **Allowlist architecture tests.** "Only these may import the database layer" catches what a denylist never thought of.
- **Failure paths first.** Where a silent failure can hurt someone or lose money or data, test that first.
- **Speed cuts reruns, never checks.** Going faster may skip re-running tests or extra review rounds, never the tests written or the plan review.
- **The project wins.** Every skill reads the project's own `AGENTS.md` and conventions first. Stack detail lives in `references/<stack>.md`, never in the core text.
- **Nothing outward-facing without a yes.** No post, push, PR, ad launch or message goes out unless you asked for it.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/skill-format.md](docs/skill-format.md). Run `python3 scripts/check.py` before a PR.

## Credits

The engineering plugins started from [Quaid5050/ai-engineering-skills](https://github.com/Quaid5050/ai-engineering-skills) (MIT). I rewrote and restructured them for how I work and extended the kit with my own skills. See [LICENSE](LICENSE).

## License

MIT. By [Muhammad Ahmad](https://mahmadmanzoor.com).
