# Rules for agents editing this repo

This repo is instructions that other agents will follow in other people's projects. Be exact.

## Layout
- `.claude-plugin/marketplace.json` lists the plugins. Each plugin has `plugins/<plugin>/.claude-plugin/plugin.json`.
- Skills: `plugins/<plugin>/skills/<skill>/SKILL.md`, stack detail in `references/` beside it.
- Agents: `plugins/crew/agents/*.md`. Hooks: `plugins/guard/hooks/hooks.json` and `plugins/guard/scripts/`.
- Skill shape: [docs/skill-format.md](docs/skill-format.md). Workflow map: [docs/workflow.md](docs/workflow.md).

## Commands
| Task | Command |
|---|---|
| All checks (same as CI) | `python3 scripts/check.py` |
| One check | `python3 scripts/check.py stack` (also `manifests skills agents links privacy`) |
| Validate | `claude plugin validate . --strict` |
| Try a plugin without installing | `claude --plugin-dir plugins/<plugin>` |

## Rules
1. No framework, language or vendor names in engineering `SKILL.md` files. They go in `references/<stack>.md`.
2. Every skill reads the target project first and lets the project's rules win.
3. No private data: no real people, customers, emails, internal paths, URLs, tokens. Toy examples only.
4. Never weaken a safety, privacy or testing rule to make a skill shorter.
5. A change to a plugin bumps its version in `plugin.json`, the marketplace entry and each skill's `metadata.version`, with a `CHANGELOG.md` line.
6. Every skill keeps `metadata.model` and `metadata.effort` honest: the smallest model that does the job well.
7. Work on a branch. Conventional commits. PR with checks green. CI uses GitHub-hosted runners only.
