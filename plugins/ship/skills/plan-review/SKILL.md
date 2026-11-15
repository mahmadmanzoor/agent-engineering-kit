---
name: plan-review
description: "Get an independent review of a plan while no code exists yet. A fresh plan reviewer checks it and posts the result on the issue. Questions run in a fixed order: placement (layer and file for each part), reuse (what exists, with the searches shown), the next feature (if it would repeat this work, build the generic piece now), then patterns, data, contract, failure modes, performance and tests. Runs at spec level on an epic, slice level on a slice, and fix level on a bug. A blocking finding holds the branch until the plan is revised. Never trimmed to save time. Say: 'review the plan before I build', '/ship:plan-review', 'is this plan right', 'review this design', 'architecture review'."
argument-hint: "[plan text, spec file, or issue #]"
license: MIT
metadata:
  version: "1.0.0"
  model: opus
  effort: high
---

# Plan review

Review the plan behind `$ARGUMENTS` (issue, spec, or a plan pasted in chat) before the branch holds any production code. With no argument, check the plan you are holding.

**Run on:** opus at high. A wrong placement passes every test, then becomes the pattern the next feature copies.

## Use it when
- You are writing a spec, starting a feature slice, or starting a non-trivial fix.
- "Non-trivial" is anything beyond a one-file change that adds no type, file, dependency or rule. A typo or a missing null check is trivial. Anything that adds a class, table, endpoint, port, adapter, provider or background-work decision is not.

**Not for:** reviewing code that is already written (`/check:review-code`).

Pick the level, which also fixes where the review is posted:
- **Spec level.** The whole technical design that `/ship:write-spec` produced. Post on the epic. For a one-slice feature, post on the docs issue.
- **Slice level.** What one slice adds. It may be brief and point to the spec-level review, but it must still answer questions 1 to 3. Post on the slice issue before the slice's first production commit.
- **Fix level.** Where a non-trivial bug fix lands, and whether the class of bug needs a shared fix. Post on the bug issue. A reproduction test may already be committed.

## Before you start
- Read `AGENTS.md`, the conventions and placement table (`/ship:code-placement`), decision records, and the stack rules of every area in play.
- Open the issue, the relevant spec section and the code about to change. Every name, path and API the plan leans on must exist or be clearly marked new.

## Steps
1. **Choose who reviews.** Start `crew:plan-reviewer` in a fresh context. Give it exactly three inputs: the issue or spec link, the plan, and `AGENTS.md`. Keep it blind to the chat that produced the plan. Without subagents, review it yourself as its own labelled step, and write in the comment that it was not independent. Do not merge this with the code review.
2. **Work through the questions in order.** Answer the first three fully every time.
   1. Placement. For each part, name the layer and file, using the placement row for its kind. A part with no matching row is a design question. Settle it now.
   2. Reuse. Is there already a port, adapter, helper, component, provider or shared rule that does this? Name it. If you found none, list what you searched: terms, rows, shared folders.
   3. The next feature. Imagine the next feature of this kind. Would it have to build the same thing again, such as another storage class for its own data, a second import reader, or a pasted copy of a rule? If yes, design the shared piece now.
   4. Patterns. State the problem each solves. Drop anything speculative.
   5. Data. Tables, constraints, indexes, and how released clients migrate.
   6. Contract. Endpoints, error codes, compatibility with installed clients.
   7. Failure modes. Offline, retry, duplicate, race, crash midway. Name the safety-critical paths.
   8. Performance. Hot paths, budgets, calls inside loops.
   9. Tests. Which seam proves each criterion? Could any part trip the architecture tests? Their baselines start empty, so the plan must not need an entry.
3. **Write it up.** Keep the heading text exact, since other skills look for it.
   ```markdown
   ## Design review — <YYYY-MM-DD>
   Reviewed: <link or one-line summary of the plan>
   Reviewer: plan reviewer (independent), or author (not independent)

   ### Decisions
   - The plan commits to <choice>, because <reason>.

   ### Reuse
   - <Existing piece> serves <part>. Or a new shared piece, <name>, replaces a per-feature one.
   - Search record: <terms and folders tried>

   ### Risks (ranked)
   - <Risk>. Failure scenario: <what breaks, concretely>. Change to the plan: <fix>.

   ### Questions for the owner
   - <question, or None>

   ### Costly-to-reverse choices
   - <choice>. It needs a record from /kit:decision.

   ### Open design findings
   - [blocking] <finding>, or None
   ```
4. **Post it.** Write the text to a scratch directory outside the repo and test it against the project's attribution policy. Post it as a single comment: `gh issue comment <n> --body-file <file>`. On the project's own issue this required review needs no further OK. Anywhere else, ask first.
   **Stop if:** any blocking finding is open. Revise the plan and update the review until none remains.
5. **Afterwards.** The build follows the decisions made here, and any deviation is explained in the PR. In its design pass, `/check:review-code` compares the diff with this review. `/ship:merge-gates` confirms the review was posted before the first production commit.

## Done when
- [ ] The review is posted on the right issue, and you can link it.
- [ ] It answers placement, reuse and the next feature.
- [ ] Every finding comes with a scenario.
- [ ] Open blocking findings: None.

## Never
- Skip or shorten it to go faster. You may trim test reruns and review rounds, but not this.
- Write code or edit repo files during the review.
- Guess a business rule that appears nowhere in the issue, spec or code. Ask the owner.
- Review the author. Review the plan.

## Next
- **Comes from:** `write-spec`, `start-issue`, `feature`, `fix-bug`, `build` (ship)
- **Leads to:** `build` (ship); checked by `review-code` (check) and `merge-gates` (ship)
