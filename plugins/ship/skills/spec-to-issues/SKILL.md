---
name: spec-to-issues
description: "Split an approved spec into an epic and its sub-issues. Slices are vertical, each usable end to end, and sequenced by risk: safety and technical first, then dependency, then learning, then the rest. Research becomes a spike. Every must requirement and every safety failure mode belongs to some slice. The full breakdown and every issue body go to the owner for approval before anything is created. Then create, link, save a manifest and open the docs PR. Say: 'break this into issues', '/ship:spec-to-issues', 'make an epic', 'slice this spec', 'create the issues for this feature'."
argument-hint: "[spec path, NNN or slug]"
license: MIT
metadata:
  version: "1.0.0"
  model: sonnet
  effort: medium
---

# Spec to issues

Take the approved spec behind `$ARGUMENTS` (path, `NNN` or slug). Produce an epic plus a sub-issue for each vertical slice, and finish by opening the docs PR. If nothing was passed, ask which spec.

**Run on:** sonnet at medium. The spec already holds the decisions. What remains is careful slicing and filing.

## Use it when
- A spec says `status: approved` and the feature needs more than one slice.

**Not for:** a spec that is not approved (`/ship:write-spec`), or a feature with a single slice (`/ship:file-issue`).

## Before you start
- Read `AGENTS.md` for the tracker, labels, milestones and what each priority means.
- Open `docs/specs/<NNN>-<slug>/spec.md`. It must say `status: approved`. If it does not, stop and ask. Read `investigation.md` as well: an approach it rejected must not come back inside an issue.
- Search for issues that already exist, so nothing is filed twice: `gh issue list --search "<slug> in:title,body" --state all` (or the project's tracker).

## Steps
1. **Slice the spec.** Once merged, every issue must hand someone a working result from end to end: screen, API, data and platform as needed. Do not make one issue per layer.
   - Wrong, by layer: add a `notes` table; add a notes API; add a notes screen.
   - Right, by slice, riskiest first: a user saves a note and sees it after a restart; a save survives a dropped connection without a duplicate; the user searches notes; the user shares one; the user edits and deletes.
   The opening slice may be plain, but it runs end to end and removes the biggest risk. If something must be researched before a slice can be designed, make it a spike: type chore plus `spike`, with a time limit. Its output is a decision recorded in the spec, not merged code.
   Risk order: first what is least certain to work (safety, technical); next what others depend on (schema, contract); next what tests an assumption; last the other normal flows, edge cases and polish.
   Name the requirements each slice covers.
   **Stop if:** a must requirement or a safety failure mode lacks an owner slice. List each one beside its slice and close the gaps.
2. **Present for approval.** Show the table, then each issue body in full.
   ```
   ## Issue breakdown: <Feature>  (spec: docs/specs/NNN-slug/spec.md)
   Why this order: <one sentence>
   | No. | Title | Requirements | Priority | Risk it retires | Areas | Flags |
   | 1 | feat(notes): save a note and see it after restart | R1, R4 | P1 | write lost on retry | server, client | safety-critical |
   Epic: "<Feature>", <n> sub-issues
   ```
   Priorities: any must in the slice makes it `P1`; should only makes it `P2`; could only makes it `P3`. Keep `P0` for urgent bugs and incidents, not planned work. The epic inherits the highest slice priority.
   Write bodies from the `/ship:file-issue` template, with the privacy check done. The owner approves the table and the bodies together. A table alone is not approval.
   **Stop if:** the owner has not approved. Revise and show it again on request.
3. **Create everything.**
   1. Confirm the label set exists (the `/ship:new-repo` labels; ask the owner the first time). Create `feature:<slug>`.
   2. Create the epic here, unless `/ship:write-spec` already made one for the plan review. In that case update it and do not make a second. Title it with the feature name. Labels: `type:epic`, `feature:<slug>`, the top priority. Set the milestone. Body: spec link, two or three sentences on the problem, and the ordered slice list. Attach the docs issue from `/ship:feature-research` as a sub-issue.
   3. File each slice with `/ship:file-issue --parent <epic>`, using the approved title, body and labels, in order. The earlier approval covers this, so do not ask again and do not edit bodies. Where an existing issue fits, link it rather than making a new one.
   4. Verify the attachments: `gh api repos/<owner>/<repo>/issues/<epic>/sub_issues --jq '.[] | "\(.number) \(.title)"'`
   5. Put `epic: <number>` in the spec front matter. Write `issues.md` as the table again, now with real issue numbers and links. Commit both to the docs branch.
   6. Open the docs PR through `/ship:open-pr`. It carries the investigation, the spec and `issues.md`, and says `Closes #<docs issue>`. A docs PR already open gets a push instead. No slice starts before it merges.
4. **Report.** Link the epic and the docs PR. Count sub-issues per priority. Name the issue to start first once the docs PR merges (`/ship:start-issue`).

## Done when
- [ ] Each must requirement and each failure mode maps to a slice.
- [ ] The owner approved table and bodies before any issue existed.
- [ ] The tracker's sub-issue list matches `issues.md`.
- [ ] The epic number is in the spec front matter.
- [ ] The docs PR is open.

## Never
- Create issues without approval, or re-create ones that already exist.
- Accept slice criteria that cannot become failing tests. A slice's "Tests to write first" must be writable from its criteria alone.
- Let a bug found mid-feature bypass the epic. File it with `/ship:file-bug --parent <epic>`.

## Next
- **Comes from:** `write-spec` (ship)
- **Leads to:** `file-issue` per slice, `open-pr` for docs, then `start-issue` on slice 1 (ship)
