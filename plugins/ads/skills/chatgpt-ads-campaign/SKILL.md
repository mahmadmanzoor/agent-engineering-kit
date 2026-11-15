---
name: chatgpt-ads-campaign
description: Create and verify new campaigns, ad groups, and ads in ChatGPT Ads Manager using browser control. Use for campaign builds and resuming interrupted drafts, including creative uploads. Does not cover Meta Ads or performance reporting.
license: MIT
metadata:
  version: "1.0.0"
  model: opus
  effort: medium
---

# ChatGPT Ads campaign

Build the requested campaign in the correct live account, then reopen and verify what actually saved. Use the user's requested structure, creative direction, destination, budget, and final state. In ChatGPT Ads, an “ad set” is an **ad group**.

Read [browser-workflow.md](references/browser-workflow.md) when beginning the account work. Read [recovery-and-verification.md](references/recovery-and-verification.md) before recovering a partial save and when doing the final readback.

## Establish the build

Recover choices and authorization from the current conversation and existing task artifacts before asking anything. Collect only missing decisions that affect the build:

- Correct account and destination/offer.
- Campaign objective; groups/themes and number of ads per group.
- Budget amount, currency, daily versus total, and campaign versus group allocation.
- Included countries and any requested exclusions, platforms, audiences, or schedule.
- Existing creatives versus requested generation, and desired text-customization behavior.
- Draft/review state or explicit launch instruction.

Never launch, publish, activate or raise spend on a campaign without the user's explicit OK in the conversation for that exact action and budget. Creating a campaign does not itself mean launching it. Save an unpublished draft when launch is not requested. Preserve any explicit review-before-upload or review-before-publish gate. Carry existing launch authorization forward; do not ask for it again unless the scope changes or the current browser action requires separate confirmation, such as accepting terms.

Inspect the current account and supported fields before promising a setup. If the user asks for per-group budgets but the UI exposes only campaign budgets, obtain their choice before changing the allocation or campaign count. A shared total cannot guarantee equal spend per group. Continue preparing copy and assets while that decision is pending.

Choose an objective that fits the requested outcome and verified measurement. Do not attach a convenient-looking conversion event without confirming its meaning and source. If the user specifically requires conversion optimization and the required event is unavailable, explain the dependency instead of silently substituting Clicks. Measurement installation is a separate scope.

## Prepare one source of truth

For multiple ads, keep a local manifest before repetitive entry. A practical campaign folder holds:

- Campaign/account identity, requested settings and final state; distinguish proposals from saved values.
- Stable local group/variant IDs and expected parent-child mapping.
- Each ad's internal name, exact public title and description, destination and tracking.
- Each group's context hints, URL, bid settings and tracking.
- Original image paths, dimensions, hashes, and generation prompts/provenance when applicable.
- Save checkpoints and platform IDs as they become available; unknown IDs stay null.

Read the actual destination to ground claims and click expectations. Use current field limits from the form; do not bake past limits into the skill. Keep variations meaningfully distinct within the user's brief. Context hints describe relevance; they are not exact-match targeting guarantees.

If images are requested, use the available image-generation skill/tool and follow its delivery rules. Do not generate new images when supplied assets already satisfy the request. Inspect originals, text spelling, card-size readability, and the platform crop. Keep exact image-to-ad mapping. Use applicable project copy-review instructions without imposing a named reviewer on unrelated projects.

## Execute through browser control

In Claude Code, use Claude in Chrome (`mcp__claude-in-chrome__*`, in the Chrome profile signed in to the ad account) or the built-in browser (`mcp__Claude_Browser__*`), following the user's choice. In Codex, use `mcp__cua_repl` and its documented APIs. The Playwright snippets in the references are Codex examples: do the same steps with the Claude browser tools (read_page, find, computer, form_input, file_upload). Do not substitute direct HTTP requests, hidden application state, CDP, or a separate browser automation runtime for this browser-control task. Local tools can prepare assets, compare readbacks, and write receipts.

Use one browser operator. Other agents may prepare assets or independently compare saved evidence; they must not concurrently edit the same wizard.

1. Confirm authentication and account identity. Inspect matching campaigns/drafts before creating one; reconcile earlier attempts or resumes by identity and contents, not name alone.
2. Create the campaign or resume the identified draft. Set the authorized campaign settings.
3. Create the requested groups and their ads, retaining the manifest's mappings and exact reviewed fields.
4. Upload the matching images through the visible UI and verify each selected image/crop. Read values after filling, before switching entries.
5. Save the draft serially and wait for a completed result. Record progress so interruption does not trigger duplicate creation.
6. Reopen the saved campaign, then perform the verification below. A successful click or toast is not a persistence check.

Batch deterministic actions where useful, but get fresh UI state after each meaningful transition. Do not reuse another run's tab ID, accessibility IDs, generated DOM IDs, account IDs, or selectors without current evidence.

## Verify and finish

Compare the saved build to the manifest:

- Exactly the intended campaigns, groups and unique ads; actual parent-group membership, not just name prefixes.
- Every native title/description, destination, tracking field and context hint.
- Each image visibly loaded, correctly mapped and cropped; dimensions/source identities where exposed.
- Reopened objective, conversion event if used, countries, budget level/type/currency/amount, schedule, platforms, audiences and text customization.
- Actual draft/published/enabled/review/serving states, reported separately.

If settings disagree across surfaces, inspect the reopened editable/detail view and record the discrepancy. Do not claim the intended value persisted when the reopened value differs. Bound retries to state-changing recovery; stop repeating the same failed mutation once the same failure recurs without new evidence.

Before an authorized launch, finish the reviewable build and resolve consequential setting mismatches. If the final button accepts terms, follow the current browser tool's confirmation requirement at that action; explain that specific reason. Never publish merely to repair a draft, unlock a control, or test an import. Reopen after publication/activation if performed; enabled does not prove Serving.

Deliver a concise result with exact counts, verified settings, current state, and any unresolved difference. Retain a receipt, saved readbacks, local manifest, relevant screenshots and creative assets. Save and embed a screenshot showing the completed browser action; keep the result tab as a deliverable. Offer a gallery or ZIP when the number of creatives makes it useful, without publishing a review site unless requested.
