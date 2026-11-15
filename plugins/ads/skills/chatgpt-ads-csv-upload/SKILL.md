---
name: chatgpt-ads-csv-upload
description: Prepare, validate, upload, and troubleshoot ad-only CSV imports in OpenAI Ads Manager (ChatGPT Ads). Use for the ads-template.csv workflow, bulk ad updates or creations, and missing-current-creative import failures. Does not create full campaign workbooks or authorize campaign launch.
license: MIT
metadata:
  version: "1.0.0"
  model: opus
  effort: medium
---

# ChatGPT Ads CSV Upload

Produce a real `.csv` in the platform's ad template and, when upload is authorized, prove server acceptance and saved account state. This skill captures a browser workflow that succeeded on October 5, 2026. Verify current UI requirements rather than treating the snapshot as a permanent API contract.

## Scope and authorization

- Distinguish **prepare for review**, **upload**, and **launch**. Preparing a file does not authorize uploading it. A direct request to upload or repair an upload in a retry loop authorizes that work; do not ask for the same permission again. It does not by itself authorize activating ads, changing budgets, or publishing a campaign.
- New ads default to lowercase `paused`. Preserve the state of existing ads unless the requested change includes status. Do not turn existing live ads off merely to test an import.
- Confirm the intended account, campaign, existing parent groups, and source creative package from current evidence. Never reuse account/ad/group/image IDs from an example or another account. If the user is reviewing first, complete the local file and validation without an upload test.
- Replacing broken draft records creates additional objects. Use this recovery only when replacement creation is within the user's repair scope and the failed records are confirmed inactive; disclose the replacement and retained originals. If the user requires preserving IDs or an in-place-only repair, use the existing editor or report the blocker.
- Handle deletion/archival separately; an import repair is not blanket authorization for irreversible cleanup. Do not change or message another chat unless authorized.

## Prepare the file

1. Read [the schema and browser notes](references/schema-and-browser.md). Use the user's current template or a fresh **Ad** CSV template from Ads Manager. The bundled [ads-template.csv](assets/ads-template.csv) is the exact ten-column template verified in this session; compare it with the current platform before relying on it for a new workflow.
2. For existing objects, use a fresh **Export for edit** to establish ad/group/image IDs and values. For new ads, use real existing group IDs and leave `ad_id` blank; populate the other fields according to their schema requirements. Export parents separately when needed to verify campaign membership. Match by `(ad_group_id, ad_name)`, not title, row position, or ad name alone.
3. Preserve headers and order. Keep approved title, copy, destination, image mapping, and group mapping unchanged unless editing them is requested. Reuse a verified native `image_file_id` with blank `image_url`, or supply a supported publicly reachable image URL. A local PNG path or workbook image is not an image reference the importer can fetch.
4. Write actual UTF-8 CSV using a CSV parser/writer; quote commas, quotes, and newlines correctly. UTF-8 BOM is accepted by the bundled helper and was accepted by the tested importer. Keep review comments, approvals, formulas, and extra sheets in a separate review artifact. Do not rename an XLSX to CSV or present a review XLSX as the upload file.
5. Run the local helper against the intended mode:

   ```sh
   python3 scripts/ad_csv.py validate /absolute/path/ads.csv --mode update
   python3 scripts/ad_csv.py validate /absolute/path/new-ads.csv --mode create
   ```

   Run from this skill directory, or use the absolute helper path. `mixed` is available only for an intentionally mixed file. Read `--help` for reconciliation options. This is a local structural check, not a server-acceptance check; resolve errors before upload. If the current official template differs, adapt the workflow/helper rather than deleting new fields to satisfy an old validator.

Budget, objective, countries, context hints, and tracking parameters are not fields in this ad-only CSV. Do not claim they were imported or preserved on newly created ads. Review them separately when preparing a launch. Image approval and serving eligibility also remain separate from import success.

## Upload and verify

Use the available browser tool, with its documented APIs and fresh visible state. In Claude Code this is Claude in Chrome (`mcp__claude-in-chrome__*`, with `file_upload` for the CSV) or the built-in browser; in Codex desktop it is `mcp__cua_repl`. Run the helper as `python3 <this skill's folder>/scripts/ad_csv.py` (needs Python 3, standard library only). Prefer the relevant connected capability if the environment provides an official, documented importer covering the same operation.

1. Scope the account view to the intended campaign/groups. Record the existing count and identities, including Draft records, so unexpected creations are detectable.
2. Open **Create → Upload bulk** and choose **Ad / CSV**. The initial object type may depend on the active tab. Select the real CSV, then inspect the import preview before the final **Upload**.
3. Verify row count, valid/uploadable counts, and **Creates / Updates** against the planned operation. An update file must show zero creates. Resolve preview discrepancies before submitting. A correct preview is not completion.
4. Submit once, then wait for the completion result. Record passing/failed/total and row-level errors. If the result is partial, ambiguous, or failed, read [recovery and retry rules](references/recovery.md) before another write. Never rerun a blank-ID create file simply because a tool timed out.
5. After a successful create, export only the new records and reconcile their actual IDs back into the final CSV. The helper rejects duplicate or ambiguous matches, incomplete exports, and changed creative fields. Preserve the original blank-ID attempt only as a clearly named intermediate, not the final reusable upload file.
6. If the task is to prove a reusable corrected CSV, test the final populated-ID file once as updates: the preview must show **Creates 0**, and the completion must pass every row. A routine successful update needs no redundant re-upload.
7. Reload and verify saved row counts, statuses/switches, names, groups, and images as relevant. Native **Export for edit** supplies the saved IDs/fields. All newly created paused ads must still be off. Reconcile any unexplained extra records before claiming completion.

Stop when the intended rows have passed and durable readback matches. If the same failure recurs after a materially different evidence-based correction, stop repeating it and identify the remaining blocker. Never activate a campaign to make a CSV test pass.

## Deliver and retain evidence

Return the final `.csv` prominently, with its row count and verified outcome. Explain what changed and distinguish imported/paused from launched/serving. If a review workbook exists, synchronize IDs and status notes without destroying feedback or image previews.

Retain a small receipt beside the output: timestamp, account/campaign scope, file hash, intended create/update counts, actual passing/failed counts, screenshot, saved IDs or native export, and unresolved items. For replacements, retain an old-to-new map and disclose any original Draft records left behind. Keep account-specific data in task outputs, not this reusable skill. Do not leave the user with blank-ID create files as the recommended file for future updates.
