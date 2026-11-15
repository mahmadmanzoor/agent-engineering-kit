# Using the kit outside Claude Code

Each skill is a standard [Agent Skills](https://agentskills.io/specification) folder. Only the plugin wrapper (manifests, hooks, namespaced agents) is Claude Code-specific.

## 1. Copy or link the skills

```bash
git clone https://github.com/mahmadmanzoor/agent-engineering-kit
cd agent-engineering-kit
scripts/install-skills.sh <skills-folder> [--link] [--only ship,check,server]
```

Common folders (check your tool's docs, they move):

| Agent | Project | Personal |
|---|---|---|
| Shared (many agents) | `.agents/skills/` | `~/.agents/skills/` |
| Codex | `.agents/skills/` or `.codex/skills/` | `~/.codex/skills/` |
| Cursor | `.cursor/skills/` | `~/.cursor/skills/` |
| Gemini CLI | `.gemini/skills/` | `~/.gemini/skills/` |
| GitHub Copilot | `.github/skills/` | `~/.copilot/skills/` |

`--link` uses symlinks, so a `git pull` in the clone updates every project.

After a flat install, plugin prefixes like `ship:` do not matter. Agents find a skill by its name.

## 2. Tell the agent to use them

Add to the project's `AGENTS.md`:

```markdown
## Workflow
Follow docs/workflow.md from https://github.com/mahmadmanzoor/agent-engineering-kit.
Before a step that has a skill (feature, start-issue, plan-review, build, review-code,
merge-gates, ...), load that skill and follow it.
```

## 3. Review agents without subagents

The three files in `plugins/crew/agents/` are role prompts. Where your tool has no subagents:

1. Open a new chat or session, so the reviewer has not seen how the work was made.
2. Paste the agent file's body as the first message.
3. Give it the plan (for `plan-reviewer`) or the diff and PR text (for `code-reviewer`), plus the issue link.
4. Paste its report where the skill says to post it: the issue for a plan review, the PR for a code review.

A review from the same chat that wrote the code does not count. It knows too much and checks too little.

## 4. Hooks

The `guard` hooks are Claude Code `PreToolUse` hooks. They read the hook JSON on stdin. To use the secret scan as a plain git hook, save this as `.git/hooks/pre-commit` in your repo and make it executable:

```bash
#!/usr/bin/env bash
echo '{"tool_input":{"command":"git commit"}}' | bash /path/to/agent-engineering-kit/plugins/guard/scripts/block-secret-commit.sh
```

See `plugins/guard/README.md` for what each script blocks.
