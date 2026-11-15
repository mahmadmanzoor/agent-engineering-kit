---
name: write-spec
description: "Produce a feature spec and see it through to approval: problem, designs and states, ranked requirements with checkable criteria, API, data, client and background behaviour, failure and privacy cases that become criteria, rollout, risks and open questions. A fresh agent reads the draft, and the plan reviewer always checks the technical part before approval. Use for work across several areas, schema changes, safety-critical paths or privacy-relevant features. Say: 'spec this feature', '/ship:write-spec', 'write a spec', 'technical design for', 'PRD'."
argument-hint: "[spec folder, feature, or MVP id]"
license: MIT
metadata:
  version: "1.0.0"
  model: opus
  effort: high
---

# Write spec

Author the spec for `$ARGUMENTS` as `docs/specs/<NNN>-<slug>/spec.md`. The folder and the docs branch (`docs/<docs-issue>-<slug>`) already exist from `/ship:feature-research`, so use them. If nothing was passed, ask which feature.

**Run on:** opus at high. Every slice built on a weak spec pays for it.

## Use it when
- The feature crosses areas, alters a schema, is safety-critical, or touches personal data.

**Not for:** a small, clear change (`/ship:file-issue`), or a feature that has not been researched (run `/ship:feature-research` first).

## Before you start
- `AGENTS.md`, for the spec location, the contract file, commands and tracker.
- `investigation.md` in the spec folder. If it is missing, run `/ship:feature-research`. A spec written from memory is a guess.
- The conventions and placement table (`/ship:code-placement`) and the stack rules, since the spec must name real files and patterns.

## Steps
1. **Draft the spec.** Start from this front matter, then add the sections below it.
   ```markdown
   ---
   status: draft     # draft, approved (owner said so), in-progress, shipped
   epic:             # filled by /ship:spec-to-issues
   mvp: B2           # MVP feature id
   design: [<frame ids>]
   ---
   # <Feature>
   ```
   Keep every section in the file. Under a section that does not apply, write "None".
   | Section | What goes in it |
   |---|---|
   | Problem and users | Who is hurt, and in what way. |
   | Design and states | For each frame, the states it shows. If no design exists, a state table (screen by state: what the person sees and can do) plus a low-fidelity flow. The owner approves those with the spec. |
   | Requirements and acceptance criteria | R1 to Rn, each marked must, should or could. Each has criteria someone can check, in user language. Example: "R2 (must): a guest cannot book a slot that is already taken." |
   | API contract | Method, path, request and response shapes, stable error codes, auth, who may call each endpoint, and who may not. |
   | Data | Entities, constraints, indexes, retention. For big tables, the migration risk and an expand, migrate, contract plan. |
   | Client | Each screen and its states, the place the code lands under the client's conventions, routes, how it behaves offline, new strings. |
   | Server jobs and scheduling | The trigger, the idempotency key, what the job re-checks at run time, time zones, and how a deploy affects it (`/server:add-job`). |
   | Platform and background work | Background tasks, permissions, widgets and push. State the battery cost you expect and how you will measure it. |
   | Files and uploads | Size limits, metadata stripping, and when the parent record counts as complete (`/server:add-upload`). |
   | Safety failure modes | Run each critical action through these cases: airplane mode, process killed, permission pulled, server unavailable, a repeated event, an event that arrives late. One test per case. |
   | Privacy and abuse | Who sees what, consent, what the person concerned can see, how long data lives, what is never logged or passed to outside parties, and how the feature could be turned against someone. |
   | Analytics | Event names, and which properties each may carry (`/check:analytics-event`). |
   | Performance budgets | One number per hot path. |
   | Rollout and rollback | Whether a flag guards it, the release path, the order of migration and backfill, and how to turn the feature off. |
   | Risks and open questions | Ranked risks, each with the step that retires it (spike, test or device test). Product questions, each with an owner. |
   | Out of scope | What the feature deliberately leaves alone. |

   A small example from a booking system. Requirement: "R3 (must): a guest who loses signal mid-booking never ends up with two bookings." Its failure-mode row: "Network drops after submit. The client retries with the same idempotency key. The server returns the first booking." The matching test: submit twice with one key, then count one booking.

   Rules while drafting:
   - Write requirements as what a person sees, not as code.
   - Each safety failure mode and each privacy rule becomes an acceptance criterion, at minimum one.
   - Point to existing files and patterns. A brand-new pattern requires a record from `/kit:decision`.
   - Open questions stay open. Offer a recommendation and let the owner decide.
2. **Get a fresh-eyes read.** Launch a new agent and give it only the spec path and `AGENTS.md`. It looks for: untestable requirements, critical paths with no failure mode, gaps in privacy, battery or cost nobody stated, endpoints with no authorisation rule, and conflicts with the design. Apply the fixes that hold up. List the points you declined, and why, under `## Review notes`.
3. **Run the plan review.** Use `/ship:plan-review` on the technical part. `crew:plan-reviewer` does it every time, however small the spec. Merge its decisions, reuse notes and risks into the spec.
   - A feature with several slices: post the review on the epic. If there is no epic yet, create it first through `/ship:spec-to-issues`.
   - A feature with one slice: post it on the docs issue.
   - Every slice later gets its own short review, before its first production commit (`/ship:start-issue`).
   **Stop if:** any design finding remains open. That blocks approval.
4. **Get approval.** Show the owner the requirements, the top three risks and the open questions, and the state table with its flow when no design exists. Mark `status: approved` only once they say yes, then commit it as `docs(specs): <feature> spec`. After that:
   - Several slices: `/ship:spec-to-issues` runs first and adds `issues.md`. Afterwards `/ship:open-pr` opens the docs PR. The PR closes the docs issue. It never closes the epic.
   - One slice: `/ship:file-issue` first, then the docs PR.
   Slices wait for the docs PR to merge. The one exception is a slice that pins the spec commit it was planned from.

## Done when
- [ ] No section is blank: each has content or says None.
- [ ] Every safety failure mode and privacy rule has an acceptance criterion.
- [ ] The review notes and the posted plan review exist, and no finding is open.
- [ ] `status: approved` is set, after the owner said so in chat.

## Never
- Create slice issues or code before the spec is approved.
- Copy spec text into issues. Link to the section instead.
- Leave the spec stale. A decision that changes mid-build changes the spec too.

## Next
- **Comes from:** `feature-research` (ship)
- **Leads to:** `spec-to-issues` or `file-issue`, then `open-pr` (ship)
