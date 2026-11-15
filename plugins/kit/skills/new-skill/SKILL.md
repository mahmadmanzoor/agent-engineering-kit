---
name: new-skill
description: "Write a new agent skill, or fix an existing one, in the kit's house format. Gather the real workflow, commands and paths, check for overlap, draft SKILL.md with the fixed sections, push stack detail into references, then let a fresh agent dry-run it on a realistic task and close every real gap. Use when you add a skill, turn a workflow into a skill, or repair a skill that was wrong. Say: '/new-skill', 'write a SKILL.md', 'turn this into a skill', 'add a new skill', 'the skill was wrong', 'update the skill'."
argument-hint: "[workflow description, skill to update, or a lesson]"
license: MIT
metadata:
  version: "1.0.0"
  model: opus
  effort: medium
---

# New skill

Build or change the skill described by `$ARGUMENTS`. That can be a workflow description, the name of a skill to fix, or a lesson such as "the review missed X". A lesson from real work goes to `lesson` first, which calls this skill for the edit. No argument? Ask which workflow the skill should cover.

**Run on:** opus at medium. Scoping a skill and spotting gaps in a dry run both take judgment.

## Use it when
- A workflow keeps repeating and should become a skill.
- A skill gave a wrong command, skipped a step, or let a mistake through.

**Not for:** explaining why a choice was made (`decision`), or logging what went wrong (`lesson`).

## Before you start
Find out where skills live and which format rules apply:
- This kit: `plugins/<plugin>/skills/<name>/SKILL.md`, with the format in `docs/skill-format.md`.
- A project: its own skills folder (for example `.claude/skills/<name>/SKILL.md`) and its own skill guide, if any.
- Plugin skills installed in a project are a cache. Change the project's own skills instead. Send kit changes upstream through `lesson`.

Read `AGENTS.md` for the shared rules. Missing a fact? Ask once and offer to record it in `AGENTS.md`.

## Steps
1. **Scope it.** Write down four things:
   - the trigger: words people say, or an event;
   - where it runs: local, CI, staging or production;
   - what it touches: git, the tracker, code, a database, devices;
   - what it produces: code, an issue, a report, a comment.
2. **Take facts from the repo.** Open the CI files, manifests and scripts. Copy exact commands, paths and job names from them. Run read-only commands to prove they work.
3. **Look for overlap.** List the current skills and read any that sit at the same workflow step. If one nearly does the job, update it. When a rule already has an owner, link to that skill and do not paste its text.
   **Stop if:** a step has no real command or path. Label it "not wired yet" or ask. Do not make one up.
4. **Draft.** Start from this frontmatter:

   ```yaml
   ---
   name: <kebab-name>            # matches the folder; lowercase, digits, single hyphens, 64 max
   description: "<what it does>. <main steps>. Use when <situation>. Say: '/<name>', '<phrase>'."   # 1024 max
   argument-hint: "[what the argument is]"
   license: MIT
   metadata:
     version: "<plugin version>"
     model: <haiku|sonnet|opus|fable>   # smallest model that does the job well
     effort: <low|medium|high>
   ---
   ```

   The body follows in a fixed order: title line, `**Run on:**`, Use it when with Not for, Before you start, Steps (with a `Stop if:` wherever a slip is costly), Done when, Never, Next. `docs/skill-format.md` has the full shape.

   House rules:
   - The description gets the skill picked. Lead with the main use, then the phrases people say.
   - Choose model and effort by what a mistake costs. Raise effort before moving up a model.
   - Keep framework, language and vendor names out of the core text. They go in `references/<stack>.md`, linked from the body.
   - Short, plain sentences (about 20 words max), imperative steps, under roughly 200 lines. Long tables move to references.
   - Mark which actions face outward (issues, PRs, comments, releases, messages) and state that they need the user's OK.
   - Never loosen a safety, privacy or testing rule.
   - Use toy domains in examples. No real product, person, issue number, path or URL.
   **Stop if:** the core text names a stack, or any "Stop if" is a feeling and not a checkable fact.
5. **Dry-run with a fresh agent.** Hand it the skill path, `AGENTS.md` and a realistic task, such as "file a bug: a booking made offline is saved twice once the app reconnects". Tell it to walk through the skill without any outward-facing action and report:
   - steps that are ambiguous;
   - commands that fail or do not exist;
   - decisions the skill never makes, and spots where it had to guess;
   - clashes with other skills.
   Close every real gap. List the gaps you turned down and say why.
   A stack-neutral skill gets two dry runs on two different stacks. Check that nothing in the core only fits one.
   **Stop if:** a second dry run still turns up a new real gap.
6. **Validate and register.** Run the kit checks (`python3 scripts/check.py`, `claude plugin validate . --strict`) or the project's skill lint. Then update every place that lists skills: the catalogue or README, the `AGENTS.md` skill list, the plugin version and the changelog. Work on a `docs/` or `chore/` branch with a message like `docs(skills): add <name>`.

## Updating a skill
A wrong skill gets a fix on the exact line. Put the missing check at the step that would have caught the problem. Describe the failure in the commit body. Where code and skill disagree on facts, the code wins, so bring the skill in line. Changing a gate or rule that other skills lean on is a minor version bump. Removing or renaming a skill is a major one.

## Done when
- [ ] Frontmatter and body sections match `docs/skill-format.md`, and the check script passes (paste its output).
- [ ] Each command and path in the skill was confirmed in the repo.
- [ ] A fresh-agent dry run happened, and the second pass found no new real gap.
- [ ] The skill is registered wherever skills are listed.

## Never
- Never register a skill that skipped the dry run.
- Never trade away a safety, privacy or testing rule to save lines.
- Never copy another skill's rules. Link to the owner.
- Never edit installed plugin files inside a project.
- Never commit or open a PR without the user's OK, unless the request already said to.

## Next
- **Comes from:** `lesson` (kit), `postmortem` (ship), the user
- **Leads to:** `decision` (kit) when the skill encodes a costly choice
