# AGENTS.md template

Each `<...>` needs a real value. Try every command yourself before it goes in. Drop a section only when it has no meaning here. Notes on filling it in come after the template.

```markdown
# Agent rules

## What this is
<One paragraph: who the product is for and what it does. Say what counts as personal data here.>

## Where things are
- `<server>/` holds <stack>. Layers: <edge> -> <application> -> <domain>, with <persistence> and <adapters>.
- `<client>/` holds <web, mobile or both>. Folder layout follows the stack rules.
- `contracts/<api>` is the API contract. The order for changes is contract, then server, then regenerated clients.
- What exists vs what is planned: <list>. State only existing things as fact. Tag everything else "planned".

## Commands
- Start local services: `<cmd>`
- Build the server and run all its tests: `<cmd>`
- Run one server test: `<cmd with filter>`
- Analyse the client and run all its tests: `<cmd>`
- Run one client test: `<cmd>`
- Format and lint: `<cmd>`
- Regenerate the API client: `<cmd>`
- Everything CI runs: `<single check command>`

## How work flows
- Tracker: <GitHub Issues on owner/repo, or another>. No issue, no work. Work in several slices gets an epic with sub-issues. Milestones are named `A — ...`.
- Branch names: `feat/<n>-<slug>`, `fix/<n>-<slug>`, `chore/<n>-<slug>`, `docs/<n>-<slug>`. Create them from the issue.
- Commits use the conventional style (`feat(scope): ...`). Who is credited as author: <rule>.
- The PR description says `Closes #<issue>`, and copies the issue's labels and milestone.

## Reviews and merging
- Before the first production-code commit of a feature slice or a non-trivial fix, an independent plan review is posted.
- Every PR is reviewed, and the review has a separate design pass. Post both on the PR.
- Gates before merge: <copied from the merge skill and adapted>. Merged by: <the agent when the gates hold, or a person>.
- Optional policies (delete the ones that do not apply): <PR CI is off, so the check runs locally and its summary is pasted> · <checks CI does not run> · <device tests batched before release>.
- A rush can shorten test reruns and review rounds. It cannot skip writing tests, the plan review or the design pass.

## Safety-critical paths
<For example: taking a payment, sending a critical notification, background sync.> This list beats any example in a skill. A change here needs failure-path tests, never swallows an error, and comes with a PR that says how it can fail.

## Privacy
- Personal data in this project: <list>. Keep it out of logs at shipped levels, out of third-party analytics, and out of issues, PRs and test names.
- Anything that shares data about a person is opt-in and visible to them.

## Done means
1. Tests came first, and they pass. Lint is clean.
2. If the API changed, the contract is updated and clients are regenerated.
3. Screens follow the design: states, copy, tokens.
4. The PR explains the change and the testing, quoting real output.
5. Docs match reality.
```

## Notes for filling it in

- **Commands.** If a command fails on a fresh checkout, fix the setup or the command before it goes in the file. People and agents will copy it verbatim.
- **Built vs planned.** A planned feature written as fact misleads every later reader.
- **Safety-critical list.** Be specific. A vague list gets ignored.
