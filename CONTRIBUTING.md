# Contributing

Issues and PRs are welcome: fixes, sharper wording, a new stack reference, or a new skill.

## Before you open a PR

1. Follow [docs/skill-format.md](docs/skill-format.md): frontmatter with `model` and `effort`, the fixed sections, plain short sentences.
2. Run `python3 scripts/check.py` and `claude plugin validate . --strict`. Both must pass.
3. Dry-run a new or changed skill with a fresh agent on a realistic task. Put what happened in the PR.
4. Bump the plugin version (patch for wording, minor for a new skill or rule, major for a removed or renamed skill) in `plugin.json`, the marketplace entry and every skill's `metadata.version` in that plugin. Add a line to `CHANGELOG.md`.

## What I will not merge

- Stack names in a core `SKILL.md` (use `references/`).
- Real company, client or person names, or anything that looks like private data.
- A change that weakens a safety, privacy or testing rule to save lines.
- A skill that posts, pushes, spends or sends anything without asking first.
