---
name: deploy-check
description: "Audit a change before merge for how it could hurt users in production. Twelve areas: API contracts old clients still call, heavy migrations, native changes that need a store release, permissions, background and scheduler behaviour, payloads, config and secrets by environment, realtime names, flags, rollback, major dependency bumps, data exposure. The output is a verdict, a deploy order and a rollback plan. Use before merging anything that reaches clients, stored data or running infrastructure. Say: '/ship:deploy-check', 'safe to merge?', 'breaking change check', 'will old app versions break', 'pre-merge check', 'what is the deploy order'."
argument-hint: "[PR number or branch name]"
license: MIT
metadata:
  version: "1.0.0"
  model: opus
  effort: medium
---

# Deploy check

Audit `$ARGUMENTS` (a PR or branch; if none, the current branch) for what could break real users once it ships. The clients are the hard part: old app versions stay installed for months and keep calling the API, and browsers hold old bundles open for hours.

**Run on:** opus at medium. If a breaking change slips by, users pay for it, so judgment matters.

## Use it when
- The diff touches an endpoint, stored data, native code, settings, schedules or infrastructure.
- You must produce a deploy order or rollback plan.

**Not for:** delivering the build (use `release`) or a privacy review (use `security-review`, check plugin).

## Before you start
Read AGENTS.md and the repo to locate: the API contract, the migration folder, native and bridge definitions, permission manifests, infrastructure and environment config, and the release paths (`release`). Also learn the oldest client version you still support and the list of environments.

```bash
git diff --stat origin/main...HEAD
git diff origin/main...HEAD -- '<contract>' '<migrations>' '<bridge defs>' '<manifests>' '<infra/config>' .github/
gh pr diff <PR> --name-only
```

Quote pathspecs that contain `**`: a few shells expand a bare glob and stop when it matches nothing.

## Steps
1. **Go through every area.** Give each area one mark: *n/a*, *safe* or *needs action*. For *needs action*, write the action. Each entry lists the risk, then the response.
   1. **API contract.**
      - Risk: a path, field or enum value disappears or changes name; a field turns mandatory; a type or error code shifts.
      - Do: only add, for as long as released clients use the contract. To retire something, leave the old shape in place until the oldest supported client has stopped calling it, or put the new shape under a new path version. Itemise each non-additive change you see in the contract diff.
   2. **Migrations.**
      - Risk: a table rewrite or long lock; a NOT NULL column with no default; a dropped column that live code still reads.
      - Do: expand first, migrate data next, contract last, one deploy each. Read the SQL that gets generated (`add-migration`, server plugin). Create indexes concurrently. Run backfills as jobs, outside the migration.
   3. **Native and bridge.**
      - Risk: a client calls a native method that older installed binaries lack.
      - Do: ship native code, bridge definitions, plugins and manifests through a store release, not an over-the-air patch. Write new code so it still runs against an older native side.
   4. **Permissions.**
      - Risk: the app asks for a new OS permission or usage text.
      - Do: plan a store release that includes review notes, a refreshed permission explanation screen, the privacy policy and the store data forms.
   5. **Mobile background behaviour.**
      - Risk: sync timing, background tasks or foreground services change.
      - Do: run `device-test` (mobile plugin) and note the battery cost.
   5b. **Server scheduling and workers.**
      - Risk: a changed schedule or job, two schedulers alive during a rolling or blue/green deploy, workers killed mid-job.
      - Do: run a single scheduler at any time, through a lock or leader election. Jobs must be idempotent, with a unique sent-ledger (`add-job`, server plugin). Let workers drain before they stop. Old and new workers must both be able to read each job payload.
   6. **Push and message payloads.**
      - Risk: older clients fail to parse the new payload.
      - Do: add fields, nothing else. Clients ignore message types they do not know.
   7. **Config and secrets.**
      - Risk: a new setting is missing from one environment.
      - Do: add a placeholder to the example env file, set the real value in each environment before deploying, and make the service refuse to start without it. Behind a reverse proxy, the trusted-proxy setting must name that proxy. Without it, all callers look like one address and split a single rate-limit budget. Do not trust any network that clients can send from.
   8. **Realtime.**
      - Risk: a socket method, channel or event is renamed, or a token sits in a URL query string.
      - Do: apply the API rule: add, never rename, until old clients are gone. Before the first deploy, remove or mask query-string tokens in every proxy, load balancer and access log.
   9. **Feature flags.**
      - Risk: a risky behaviour reaches 100% of users at once.
      - Do: put safety and privacy changes behind a flag or a staged rollout when you can. Write the removal condition for each flag.
   10. **Rollback.**
      - Risk: nothing lets you undo it.
      - Do: name the route back: revert and redeploy, roll back the patch, or halt the staged rollout. For migrations, state whether the down path is tested or whether you will roll forward instead.
   11. **Dependencies.**
      - Risk: a dependency jumps a major version.
      - Do: read its changelog, then run each build it touches. If the dependency is native, plan a store release.
   12. **Data exposure.**
      - Risk: a new field, endpoint or log statement exposes personal data.
      - Do: run `security-review` (check plugin).

   **Stop if:** an area is unmarked.
2. **Write the verdict** in this shape:
   ```markdown
   ## Deploy check: <PR>
   Reaches users via: server deploy, web deploy, over-the-air patch or store release (and why)
   Verdict: safe / safe with steps / not safe yet

   | Area | What I found | Action (before or after merge) |
   |---|---|---|

   Deploy order: 1. ... 2. ...
   Way back: ...
   ```
3. **Post it on the PR.** One comment, headed `## Deploy check — <short head SHA>`. It satisfies merge gate 8 (`merge-gates`).
   **Stop if:** area 1, 2, 3, 5b or 7 is unsafe. Each blocks the merge. Either fix it, or get the owner's explicit acceptance of the risk and quote it in the PR.

## Done when
- [ ] Every area carries a mark and an action.
- [ ] Verdict, deploy order and rollback plan exist in writing.
- [ ] The PR has the comment, with the head SHA in its title.

## Never
- Modify an environment, secret or deploy setting here. Record the action and its owner.
- Take the faster release path when in doubt. Take the slower, safer path.
- Post the verdict before the user agrees, if the project asks for approval on PR comments.

## Next
- **Comes from:** `open-pr`, `ci-green` (ship); `add-endpoint`, `add-migration` (server); `background-work` (mobile)
- **Leads to:** `merge-gates`, then `release` (ship)
