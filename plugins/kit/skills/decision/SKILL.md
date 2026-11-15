---
name: decision
description: "Write a short decision record for a choice that is hard to undo. Lay out the problem with file paths, two or more honest options (keeping the status quo counts), what each costs now and later, the pick, its effects and a measurable trigger for reopening it. Link the record from the rule it backs, or amend or supersede an older one. Use when taking on or rejecting a library, pattern, service or stance. Say: '/decision', 'should we switch to Y', 'why did we choose X', 'write an ADR', 'record this decision'."
argument-hint: "[the question, e.g. 'which database?']"
license: MIT
metadata:
  version: "1.0.0"
  model: opus
  effort: medium
---

# Decision

Produce a decision record for `$ARGUMENTS`, which is the question being settled. No argument? Ask which decision to record.

**Run on:** opus at medium. Judging options and lock-in is a judgment call.

## Use it when
- The team is about to take on, or turn down, something costly to undo. Examples: a library, an architecture pattern, a new service, a naming or API convention, a stance on security or privacy, a vendor you pay.
- Someone asks why a past choice was made, or wants to swap it.

**Not for:** a choice an existing convention already settles, or anything a one-hour refactor can reverse.

## Before you start
Look up:
- the records folder (`docs/decisions/`, `docs/adr/`, or the project's own), the latest record as a format model, and the next number;
- the convention or skill the choice will shape, plus earlier records on the same topic.

Missing a fact? Ask once. Offer to write the answer into `AGENTS.md`.

## Steps
1. **Check it deserves a record.** Hard to reverse, or the reasoning is easy to forget? Then yes.
2. **Collect the evidence.**
   - State the problem as it appears in this repo, with paths, and who pays for it: users, battery, money, privacy, the team.
   - Name two or more real options. "Leave it as is" counts. Per option, record the cost today, the cost later, what it ties you to, and one authoritative source (official docs before blogs).
   - Is this a revisit? Test the old record's reopen trigger against evidence. If it has not fired and nothing else is new, the verdict is "keep": add a dated note to the old record and stop.
   - Note every edit the choice forces: conventions, manifests, generators, lint config, other records.
   **Stop if:** the choice adds or drops a dependency, alters product behaviour, touches safety-critical code or privacy, or brings in a paid service, and the owner has not agreed in this conversation. Quote the agreement in the PR.
3. **Write the record** at `docs/decisions/NNNN-<kebab-slug>.md`, numbered with the next free four digits.

   ```markdown
   # NNNN - <the choice, as one short sentence>

   Status: proposed, accepted, amended by NNNN, or superseded by NNNN (<YYYY-MM-DD>)

   ## Problem
   <3-6 lines of situation and pressures, with paths>

   ## Options
   | Option | Pros | Cons |
   |---|---|---|
   | <A, picked> | ... | ... |
   | <B> | ... | ... |
   | Leave it as is | ... | ... |

   ## Choice
   <One paragraph. What we do. What we do not do.>

   ## Effects
   - <easier / harder; follow-up work with issue links>

   ## Reopen when
   <a measurable trigger: size, version, cost, pain>

   ## Sources
   - <title>: <url>
   ```

   A record that ships in the same change as the work it decides is `accepted` from the start, because merging is the acceptance. Use `proposed` only if the record goes up for discussion first.
4. **Connect and land.**
   - Point to the new record from the convention or skill whose rule it backs.
   - Old record fully replaced: set its status to `superseded by NNNN`. Only one line of a multi-choice record changes: write a fresh record for that line, set the old status to `amended by NNNN`, and say which line it overrides. Cross-link both ways. Records stay in the repo for good.
   - Do the follow-up edits in this change, or file issues and link them under Effects.
   - Ship it like any change: issue, branch, PR, then `review-code` (check plugin).
   **Stop if:** the reopen trigger is missing or vague ("later"). Name something measurable.

## Done when
- [ ] Every section is filled and at least two real options appear (one may be "leave it as is").
- [ ] Each option lists a cost now, a cost later and a source.
- [ ] The reopen trigger is measurable.
- [ ] The convention it explains links to it, and any older record links both ways.

## Never
- Never drop an option without a stated reason.
- Never record two decisions together. If choices are tied together, give each its own line in one record so any of them can be amended alone.
- Never let a record loosen the project's rules on safety, privacy or testing.
- Never delete a record.
- Never open the PR without the user's OK, unless the request already said to.

## Next
- **Comes from:** `new-repo` (stack choice), `plan-review` (costly-to-reverse choices), `write-spec` (ship), the user
- **Leads to:** the convention or skill it shapes
