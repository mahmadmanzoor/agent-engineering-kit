---
name: file-issue
description: "Create one issue for a feature slice that is already scoped, from a fixed template. Title names the outcome in conventional-commit form. Header lines give design frame, MVP id, milestone, priority, areas and flags (safety-critical, privacy, needs-device-test). The body holds summary and reason, 3 to 7 testable acceptance criteria with failure states, tests to write first, out of scope, approach and open questions. A privacy check precedes the owner's approval, and the issue can join an epic. Say: '/ship:file-issue', 'file this feature', 'make an issue for this', 'raise a feature issue', 'track this work as an issue'."
argument-hint: "[feature in one line | design frame | --parent <epic> plus description]"
license: MIT
metadata:
  version: "1.0.0"
  model: sonnet
  effort: low
---

# File issue

Turn `$ARGUMENTS` into an issue. It may be a feature in one line, a design frame, or `--parent <epic>` followed by a description. Without an argument, ask for the feature in a single line.

**Run on:** sonnet at low. A fixed template and an already-clear slice.

## Use it when
- The slice is scoped: you can say what a person gains and how to see that it works.

**Not for:** a vague goal, competing approaches or several risky areas (`/ship:feature-research`, then `/ship:write-spec`), and not for bugs (`/ship:file-bug`).

## Before you start
Read `AGENTS.md` and note the tracker and repo, labels, milestones, priority definitions and where specs live. If labels are missing, offer the script from `/ship:new-repo`. It changes the repo, so ask first.

When `/ship:spec-to-issues` calls this skill, everything is already approved. Ask nothing and change nothing outside the issue.

## Steps
1. **Fill in the fields** using the conversation, spec and design as sources. You may ask one question at most, and only about something you cannot infer. That is usually priority.
   - **Title:** conventional commit style, 70 characters or fewer, naming the outcome a user sees. Good: `feat(shop): customer sees an order receipt after paying`. Bad: `add receipts table`.
   - **Design:** the frame id and title as the design source shows them. With no design, point to the state table and flow the spec has approved. If those are unapproved too, add the `needs-design` label: work on the slice must wait.
   - **MVP item:** the feature id and milestone, or `post-MVP`.
   - **Priority:** `P0` to `P3`, following the project's definitions.
   - **Blocked:** the labels `blocked` and `blocked:<reason>`, plus a `**Blocked by:**` line.
   - **Areas:** an `area:*` label per module the slice touches.
   - **Flags:**
     - `safety-critical` when the project's list includes it, or when a silent failure could hurt a person, cost money or destroy data.
     - `privacy` for personal data, sharing or consent.
     - `needs-device-test` for background work, notifications, widgets, battery or hardware.
   - **Summary and reason:** one or two sentences each, with a link to the spec section.
   - **Acceptance criteria:** 3 to 7 checkable bullets in the user's language. Include the failure states: offline, permission denied, empty, error.
   - **Tests to write first:** derived from the criteria and written from the caller's side (a UI test, an API integration test or a domain unit test). If a criterion cannot become a failing test, it is not ready, so rewrite the criterion.
   - **Approach:** one short paragraph naming likely folders and patterns to copy. It is not a design doc.
2. **Draft the body.** Keep this template as is. Do not add or remove a section. Write "None" for an empty one.
   ```markdown
   **Spec:** docs/specs/<NNN>-<slug>/spec.md#<section> · **MVP:** <id · milestone> · **Design:** <frame>
   ### Summary
   ### Reason
   ### Acceptance criteria
   - [ ] <what the user can observe>
   ### Tests to write first
   - [ ] `<test path>` proves <behaviour>
   ### Out of scope
   ### Approach
   ### Open questions
   <details><summary>Context</summary>Related links: spec, investigation, other issues, design.</details>
   ```
   Run the privacy check before the preview. Keep real names, addresses, phone numbers, emails, coordinates and account ids out of the title and body, and use no screenshots of real data. Say "User A" and "User B" or use made-up ids.
3. **Preview and get approval.** Show the owner everything: title, labels, milestone, parent, body.
   **Stop if:** the owner has not approved. Words like "file it" in the original request already count as approval.
4. **Create the issue.** Save the body to a file first.
   ```bash
   gh issue create \
     --title "<title>" --body-file <file> \
     --label "type:feature,P1,area:server" --milestone "<milestone>"
   # the epic link needs the child's numeric id, which is not its number
   gh api repos/<owner>/<repo>/issues/<child> --jq .id
   gh api repos/<owner>/<repo>/issues/<epic>/sub_issues \
     -X POST -F sub_issue_id=<id>
   ```
   The last two lines apply only when you got `--parent` or the spec names an epic. If the child already has another parent, you need `replace_parent=true` plus the owner's OK. For other trackers, use their create and link-to-parent calls.
5. **Report** four things: the link, the labels, the parent, and which test to write first. When the spec has an `issues.md`, add a row for the new issue.

## Done when
- [ ] The issue matches the template and every section is present.
- [ ] It lists 3 to 7 criteria, each of them testable.
- [ ] The privacy check passed.
- [ ] The owner approved before creation.
- [ ] If an epic exists, the issue is linked to it, and you confirmed that in the tracker.

## Never
- Split a slice by layer into "add the table", "add the endpoint", "add the screen".
- Create, label or link before approval.
- Change someone else's issue without being asked.
- Create `feature:<slug>` labels here. `/ship:spec-to-issues` does that.

## Next
- **Comes from:** `feature-research`, `write-spec`, `spec-to-issues` (ship), the conversation
- **Leads to:** `start-issue` (ship)
