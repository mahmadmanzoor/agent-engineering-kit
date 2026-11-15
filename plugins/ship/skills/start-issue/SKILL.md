---
name: start-issue
description: "Get an issue ready for coding. Read it along with its epic, spec and design, and send it back if acceptance criteria or first tests are absent. Branch through the tracker so branch and issue stay linked, write a plan, and have an independent reviewer post a plan review on the issue before any production code is committed. Then assign the issue and pass it to build. Say: 'set up a branch for', 'start issue', 'pick up issue', '/ship:start-issue', 'work on #', 'begin this ticket'."
argument-hint: "[issue number or URL]"
license: MIT
metadata:
  version: "1.0.0"
  model: sonnet
  effort: medium
---

# Start issue

Work issue `$ARGUMENTS`, given as a number or URL. With no argument, list what is open and assigned to the user, and ask them to choose.

**Run on:** sonnet at medium. It is bounded setup work with clear gates.

## Use it when
- An issue is ready to be picked up.

**Not for:** filing issues (`/ship:file-issue`, `/ship:file-bug`) or building the change (`/ship:build`).

## Before you start
Pull these from `AGENTS.md`: the tracker and repo, branch naming, worktree policy, which changes are non-trivial, and the merge gates.

## Steps
1. **Read the issue and what it links to.**
   ```bash
   gh issue view <n> --json title,body,labels,assignees,state,milestone
   gh api repos/<owner>/<repo>/issues/<n>/parent --jq .title || echo "no parent epic"
   ```
   Next, follow each link: the spec section that applies, the investigation, the designs (frames, or the approved state table and its flow), the epic's plan review, and neighbouring issues. A bug's investigation report matters most.
   Hold a feature slice until the docs PR for its spec has merged. When the owner wants an earlier start, freeze the spec version: find the commit the slice was planned against (`git show <sha>:docs/specs/<NNN>-<slug>/spec.md`) and record it in the plan.
   **Stop if:** the issue is not ready.
   | Issue type | Ready means |
   |---|---|
   | Feature | Acceptance criteria and "Tests to write first" are present. No `needs-design` label is open. |
   | Bug | The expected behaviour is stated, and a regression test is named. |
   | Docs or chore | The issue says what done looks like. |
   If it fails, list the gaps for the owner and ask, or run `/ship:feature-research` or `/ship:debug`. Example of a vague issue: "Add search to the notes app". A ready one says "Search notes by title; results appear within 300 ms; an empty query shows all notes", then lists the tests.
2. **Create a linked branch.** Use `feat/<n>-<slug>`, `fix/<n>-<slug>`, `chore/<n>-<slug>` or `docs/<n>-<slug>`, matching the issue type.
   Check `git status --short` before anything else. Work for another issue, committed or not, cannot come along. Ask the owner, then move it to its own branch or a separate worktree. Skip the stash: worktrees and other sessions share a single stash.
   The branch is created from the issue, so the tracker records the link:
   ```bash
   gh issue develop <n> --base main --name feat/<n>-<slug>
   git fetch origin
   git switch feat/<n>-<slug>
   gh issue develop --list <n>    # shows the link
   ```
   Does this checkout hold other work? Add a worktree instead: `git worktree add ../<repo>-<n> feat/<n>-<slug>`. Already on a session branch? Push it, and branch from it using `--base "$(git branch --show-current)"`. Tracker other than GitHub: put the issue key in the branch name.
   For issue 42, "search notes by title", the branch is `feat/42-note-search`.
   **Stop if:** the work would land on `main`.
3. **Plan.** Short, and in the conversation. Post it to the issue only if the owner wants that.
   - Files to change, each with an existing pattern to copy, chosen by placement row (`/ship:code-placement`).
   - Skills the work will call on (`/server:add-endpoint`, `/server:add-migration`, `/mobile:design-to-screen`, `/mobile:background-work`), plus side changes: contract and regenerated clients, migrations, strings, bridges, docs.
   - The tests in the order you will write them. The first is your next move.
   - Blocked? Label it `blocked:<reason>`, comment `**Blocked by:** ...`, inform the owner, and take a different issue.
   - A device test, if the change needs one.
   For the note search, a plan might read: query function in the notes module (copy the existing list query), one endpoint with a contract update and regenerated client, a search box on the list screen. Tests, in order: the empty query returns every note, a title match returns only that note, a miss returns an empty list.
4. **Plan review before code.** Run `/ship:plan-review` when the change is a feature slice or a non-trivial fix (bigger than a one-file edit that adds no type, file, dependency or rule). `crew:plan-reviewer` then posts `## Design review — <date>` on this issue, before the first commit that holds production code.
   - If the slice belongs to a specified feature, the review can be short and link the epic's. It must still say where the code goes, what is reused, and whether the next feature would repeat this work.
   - A bug's reproduction test, or characterisation tests before a refactor, may be committed ahead of the review. Production code may not.
   - Keep revising the plan until all findings are closed.
   - If you call a fix trivial, the PR must explain why.
   **Stop if:** the review comment is not on the issue and the change is not trivial.
5. **Claim the issue.** If it is not already assigned to the owner, ask them first, then run:
   ```bash
   gh issue edit <n> --add-assignee @me --add-label in-progress
   ```
   If this is the first slice of a feature, set the spec's `status: in-progress` too.
6. **Hand over.** Give the owner a summary: issue and epic, branch, plan, review link, first failing test, key files. If they asked for the build, go straight into `/ship:build` in the right mode (`feature`, `bug` or `maintenance`). A docs issue is written next, then goes through `/ship:commit-check` and `/ship:open-pr`.

## Done when
- [ ] The issue passed its readiness check.
- [ ] `gh issue develop --list <n>` lists the branch, or the tracker shows its own link.
- [ ] The issue holds the plan review. Otherwise the change is trivial and says so.
- [ ] The plan names the first failing test.

## Never
- Start coding when the issue is vague.
- Combine two issues in a single branch or PR.
- Change labels or assignees on a shared board without asking the owner.
- Commit production code before the plan review is posted.

## Next
- **Comes from:** `file-issue`, `spec-to-issues`, `file-bug`, `fix-bug`, `feature` (ship)
- **Leads to:** `build` (ship)
