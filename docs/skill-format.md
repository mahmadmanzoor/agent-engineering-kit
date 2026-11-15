# How a skill is written here

Every skill is a plain [Agent Skills](https://agentskills.io/specification) `SKILL.md`, so Claude Code, Codex, Cursor, Gemini CLI and Copilot can all read it. On top of the spec, this kit uses one fixed shape. `scripts/check.py` checks the mechanical parts.

## Files

```
plugins/<plugin>/skills/<skill-name>/
├── SKILL.md          # required, under ~200 lines
└── references/       # optional: stack detail or long tables, one level deep
    └── <stack-or-topic>.md
```

- `name`: lowercase, digits and single hyphens, max 64 characters, same as the folder name.
- `description`: max 1024 characters.
- Link references with a relative link: `[references/node.md](references/node.md)`.

## Frontmatter

```yaml
---
name: <kebab-name>
description: "<What it does, one sentence>. <Key steps, short>. Use when <situation>. Say: '<phrase people use>', '<another>'."
argument-hint: "[what the argument is]"    # optional
license: MIT
metadata:
  version: "1.0.0"      # the plugin's version
  model: sonnet         # haiku | sonnet | opus | fable: the smallest model that does this job well
  effort: medium        # low | medium | high
---
```

`model` and `effort` say what to run the skill on. Pick by the cost of a mistake, not by how long the skill is:

| Model | Use for |
|---|---|
| `haiku` | Mechanical, cheap-to-check work: tidy-up, file lookups, running checks, summaries. |
| `sonnet` | Well-scoped work: write tests, build a screen, file an issue, open a PR, draft posts. |
| `opus` | Judgment: plan review, code review, security, debugging, migrations, incidents, specs. |
| `fable` | Large refactors, architecture for a new system, long unattended runs. |

Effort comes before model: raise effort one level before moving up a model.

## Body

```markdown
# <Title>

<One line: what this does with `$ARGUMENTS`. If empty: what to ask, or the default.>

**Run on:** <model> at <effort>. <One short reason.>

## Use it when
- <situation>
**Not for:** <what goes to another skill, and which one>

## Before you start
<Read the project first: AGENTS.md / CLAUDE.md / CONTRIBUTING.md, the stack manifest, CI files.
List the facts this skill needs (commands, paths, tracker). The project's own rules win.
If a fact is missing, ask once and offer to write it into AGENTS.md.>

## Steps
1. **<Step name>.** Short imperative sentences. Commands in code blocks, as examples to adapt.
   **Stop if:** <a checkable condition that blocks the next step>
2. ...

## Done when
- [ ] <checkable result, with the evidence that proves it>

## Never
- <hard limits: safety, privacy, things that need the user's OK>

## Next
- **Comes from:** `<skill>` (<plugin>)
- **Leads to:** `<skill>` (<plugin>)
```

## Writing rules

1. **Plain and short.** One idea per sentence, about 20 words max. Active voice. Imperative for steps. No filler words.
2. **No stack in the core.** A `SKILL.md` never names a framework, language or vendor. Say layer, port, adapter, contract, test. Stack detail goes in `references/<stack>.md`. `scripts/framework-terms.txt` lists the blocked names.
3. **Read before acting.** Never invent a path, command or tool. Find it (`ls`, the manifest, the CI file) or ask.
4. **Stop-points where a mistake is costly.** A "Stop if" names something you can check, not a feeling.
5. **Point, don't repeat.** One skill owns each rule. `test-rules` owns testing rules, `code-placement` owns where code goes. Other skills link to the owner, with its plugin name when it lives elsewhere.
6. **GitHub is the example tracker** (`gh`). Always add "or the project's tracker". Git itself is assumed.
7. **Ask before anything outward-facing:** issues, comments, pushes, PRs, releases, messages, posts. Skip the ask only when the user's request already said to do it.
8. **Never weaken safety or privacy.** Where a silent failure can hurt a person, lose money or lose data, write the failure-path tests first and never swallow errors.
9. **Generic examples.** Toy domains only: a notes app, a shop, a booking system. No real product, person, company, issue number, internal path or URL.
10. **Every claim checkable.** "Tests pass" only with the command and its output.

## Checks

- `python3 scripts/check.py`: frontmatter, names, lengths, manifests, versions, links, blocked names, privacy patterns.
- `claude plugin validate . --strict`
- A dry run with a fresh agent on a realistic task (see `new-skill`).
