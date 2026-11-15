---
name: postmortem
description: "Produce a blameless postmortem when an incident or serious escape is over. Escapes include a critical alert nobody saw, records lost or duplicated, and exposed data. The document holds a summary, who was affected, a UTC timeline, five-whys root cause, which test rung should have caught it, what helped and hurt, and follow-ups (prevent, detect sooner, mitigate) each with an issue. Then the lesson gets encoded. Use after SEV1 or SEV2 incidents. Say: 'incident review', 'retro on the outage', '/ship:postmortem', 'what did we learn', 'root cause analysis document', 'write the postmortem'."
argument-hint: "[incident slug, issue or description]"
license: MIT
metadata:
  version: "1.0.0"
  model: opus
  effort: medium
---

# Postmortem

Document `$ARGUMENTS` (an incident slug, an issue, or a description) in `docs/postmortems/<YYYY-MM-DD>-<slug>.md`, or wherever the project keeps them.

**Run on:** opus at medium. It calls for honest root-cause reasoning, not fault-finding.

## Use it when
- A SEV1, SEV2 or data-integrity incident is over (`incident`). Required.
- A bug let a critical action slip by, lost or duplicated records, or exposed personal data.
- A SEV3 touched a safety-critical path. Optional, but worth doing.

**Not for:** running the live response (`incident`).

**Blameless:** explain how systems, tests and processes allowed it. Never write who "should have" acted differently.

## Before you start
Pull together what the incident left behind: the draft timeline, the investigation notes, every PR and release involved, the signals and links from `observe`, and user reports with personal data removed. Use `gh pr view` and `git log` for the code side. Check whether the project already has a postmortem folder or template, and use it.

## Steps
1. **Draft the document.**
   ```markdown
   # <Title>: postmortem
   Level: SEV1, SEV2 or SEV3 · Issue: <link> · Date: <day> · Ran: <start> to <end> UTC · Status: draft or final

   ## At a glance
   Three sentences. First what broke, then who felt it, then how it ended.

   ## Who was affected
   Counts, platforms, versions. What they saw. Any safety effect. Damaged data and how it gets repaired.

   ## Timeline (UTC)
   - 14:02 first alert, ...

   ## Why it happened
   Ask why five times and stop at the deepest cause we control. Link the evidence for each answer.

   ## How we found out
   Name the rung that caught it and the rung that should have. The ladder lives in `test-rules` (check plugin): type or compile, lint, architecture test, unit or integration test, CI, plan review, code review, device test, alert, user report.

   ## What helped, what hurt, where luck saved us

   ## Follow-ups
   - <action> | prevent, detect or mitigate | issue link | owner | due date
   ```
   **Stop if:** an answer under "Why it happened" or "How we found out" has no evidence link, or a follow-up has no type.
2. **Turn findings into follow-ups.** Each action must catch this kind of bug sooner, or rule it out. Candidates: a stricter type, a regression test, a lint rule, an architecture test, an alert, or a new device-test row. "Be more careful" is not an action. With the user's OK, file each via `file-bug` or `file-issue`, and put the issue link in the list.
3. **Encode the lesson** with `lesson` (kit). Typical homes: a review dimension, a test rule, a placement row, a device-test row. A lesson left only in this document will be learned again the hard way.
   - Project with these skills installed as plugins: leave the plugin files alone. Record the lesson in the project itself (AGENTS.md, its conventions, architecture tests or own skills). If the user agrees, draft an upstream issue that states the lesson in general terms.
   - Kit repository itself: change the skills, bump the version and update the changelog as `lesson` describes.
4. **Close out.** Show the draft to the user, and flip the status to `final` after they agree. Commit it on a `docs/<tracking-issue>-<slug>` branch with the project's rule and test updates, then open a PR. The PR closes any follow-up issues it settles.

## Done when
- [ ] Every section has content. "Root cause unknown" is allowed, but then the investigation that finds the cause becomes follow-up number one.
- [ ] Each claim about cause and detection links to evidence.
- [ ] Each follow-up has a type, an owner and an issue.
- [ ] The lesson is encoded in the project, not just written here.

## Never
- Pin a mistake on a named person. Describe the system instead.
- Put personal data, tokens or exact locations anywhere in it.
- Mark it `final` before the user has agreed.

## Next
- **Comes from:** `incident`, `fix-bug` (ship) for a serious escape
- **Leads to:** `lesson` (kit); `file-bug`, `file-issue` (ship)
