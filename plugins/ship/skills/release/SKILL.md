---
name: release
description: "Take merged work live without harming users. Decide how each component ships: backend deploy, web deploy, over-the-air patch, or a store release when native code or permissions changed. Check preconditions, bump and tag the version with approval, widen exposure in stages with a watch window after each, and reverse course along the same path when safety or health signals fall. Use when merged changes should reach users. Say: 'cut a release', 'hotfix', 'ship it', '/ship:release', 'publish to the store', 'staged rollout', 'release a new version', 'roll back the release'."
argument-hint: "[version, PR list, or hotfix <PR>]"
license: MIT
metadata:
  version: "1.0.0"
  model: opus
  effort: medium
---

# Release

Ship what `$ARGUMENTS` names: merged PRs, a version, or `hotfix <PR>`. Your part is to prepare and verify. The user signs off on every step that reaches people.

**Run on:** opus at medium. A bad release lands on real users, and a few paths cannot be undone.

## Use it when
- Merged work needs to go live.
- A rollout is in flight and needs a watcher, or has to be reversed.

**Not for:** merging (`merge-gates`) or an outage in progress (`incident`).

## Before you start
Read AGENTS.md and the repo. Write down:
- How releases are made: the deploy pipeline, the store build commands, an over-the-air patch tool if there is one.
- Where the version number lives, and how tags are named.
- Which environments exist.
- The health signals to watch and what counts as healthy for each (`observe`).

If none of this exists, tell the user. On a first run, open a `chore(release)` issue for the setup and write the commands that work into AGENTS.md.

## Steps
1. **Pick the path.** Compare the code with the last release. The first match wins.
   - Only UI, logic, strings or already-bundled assets changed on the client, and the stack has a patch tool: **over-the-air patch**.
   - The diff has native code, bridge definitions, plugins, permissions, manifests, a new runtime version, or assets the patch tool cannot carry: **store release**.
   - A web front end changed: **web deploy**. Give asset files hashed names and cache only those for long. Never cache the entry page. Browser tabs that stay open run the old bundle for hours, so the server must stay compatible with it. If versions differ, prompt for a reload.
   - Only the server changed and its contract just grows: **backend deploy**.
   - Server and client both changed, with a contract change: ship the server first (additive, check `deploy-check`), the client second.

   ```bash
   LAST=$(git describe --tags --abbrev=0 --match '<component>-v*')
   git log --oneline $LAST..origin/main
   git diff --stat $LAST origin/main -- <native-paths> <dependency-manifests>
   ```
   Still unsure? Fall back on the client type. A mobile app's first release, or any doubtful mobile change, is a store release. Web front ends go out by web deploy, and servers by backend deploy. If the repo holds several deployable parts, choose per component.
   **Stop if:** the path is unnamed, or no diff backs the choice.
2. **Confirm preconditions.**
   - CI on main is green for the commit you will release (`ci-green`).
   - Every included PR that changes config, native code, data or an API has a passing `deploy-check`.
   - Anything touching battery, widgets, notifications or background tasks has had its `device-test` run (mobile plugin).
   - Release notes exist, written in plain words from the merged PR titles.
   - The build reports crashes and errors.
   - Mobile only: store privacy forms and the policy URL describe what the build really gathers. Each new permission has its usage text.
   **Stop if:** the commit is red or unreviewed, or a required check is missing.
3. **Version and tag.** Create `chore/release-<component>-x.y.z`, bump the version there, then open a PR and merge it. Use semantic versions. A mobile build number must never go down. After that, and only with the user's OK:
   ```bash
   git tag <component>-vX.Y.Z <sha>
   git push origin <component>-vX.Y.Z      # e.g. shop-api-v1.4.0
   ```
   A single-component repo can tag plain `vX.Y.Z`. In a monorepo, tag every component on its own, so each path stays traceable and reversible.
   **Stop if:** the user has not approved the tag.
4. **Stage the rollout.** Before each step, get the user's OK. After it, watch (`observe`) before going on.
   - **Store release:** build with the patch tool's release command if one is in use, so later patches can target the build. Upload to internal testing. Install on physical devices and work through the `device-test` smoke rows. Then widen in steps, such as 10%, wait 24 h, 50%, wait 24 h, 100%.
   - **Over-the-air patch:** first confirm that no native change landed after the release being patched. Publish to staging, test on a device, then promote.
   - **Web deploy:** deploy to a preview URL and smoke-test the main flows before production. Leave the previous build ready so you can switch back at once.
   - **Backend deploy:** push through the pipeline. Never run more than one scheduler, during or after the deploy, and never fewer. Let workers finish their jobs before they stop. Apply a migration ahead of the new code only when it is additive. Smoke-test the health endpoint and one authenticated request. Prefer canary or blue/green when offered. Detail: [references/backend-deploy.md](references/backend-deploy.md).

   Store specifics: [references/mobile-stores.md](references/mobile-stores.md).
   **Stop if:** a safety signal regresses, or a health signal ends the watch window under target. Halt and roll back.
5. **Roll back if needed.**
   - **Store build:** stop widening the rollout and ship a corrected build. People who already updated keep the bad build until that arrives.
   - **Over-the-air patch:** pull the patch back, or publish the last known good code.
   - **Web:** point production at the previous build, or redeploy it. Purge the cached entry page.
   - **Backend:** redeploy the earlier image. Fix schema problems with a forward migration. Roll one back only if that down path was tested.

## Done when
- [ ] The path and the diff that decided it are named.
- [ ] Each precondition is confirmed with evidence.
- [ ] Every rollout step had the user's OK and a clean watch window.
- [ ] The report gives the path and why, the version or build, the PR list, the rollout stage, health numbers, and the next step with its date.

Reports must show the difference between "merged", "released to x%" and "released to everyone".

## Never
- Upload, tag, promote or deploy before the user approves that exact step.
- Release a commit that is red or lacks review.
- Let an over-the-air patch bring in permissions, native code or native dependencies.

## Next
- **Comes from:** `merge-gates`, `deploy-check` (ship); `device-test` (mobile)
- **Leads to:** `observe` in every watch window; `incident` if it goes wrong (ship)
