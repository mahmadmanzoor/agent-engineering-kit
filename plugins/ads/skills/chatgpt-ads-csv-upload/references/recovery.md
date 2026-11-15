# Failed, partial, and uncertain imports

Read this before retrying an import that may have changed account state. A “retry until it works” request authorizes useful recovery attempts, not unbounded duplication or campaign activation.

## Keep a per-attempt record

Before submitting, retain the file/hash and expected creates/updates. Afterward, record row-level outcomes and export saved objects. Separate **confirmed created**, **confirmed failed**, and **outcome unknown**. Do not retry unknown creates until an account readback establishes whether they exist.

- **All rows succeeded:** stop retrying. Export/reconcile created IDs and verify saved state.
- **Partial success:** keep every successful ID. Build the next attempt only from confirmed failures; do not re-create passing rows. Reconcile individual failed rows to CSV record numbers with a parser, not physical newline counts, because quoted copy can span lines.
- **Timeout or closed dialog:** read the importer status, campaign/ad table, and fresh export before another submission. Absence from one export is not confirmed failure while the original import may still be processing. Require a terminal result or evidence that processing has settled before retrying an absent row; otherwise retain outcome unknown and stop writes. If names/IDs cannot uniquely distinguish a successful create, resolve the ambiguity first.
- **Schema/copy/image error:** correct only the reported cause, preserving approved values outside the necessary edit. If resolution would require changing approved creative intent, surface that decision rather than silently rewriting it.
- **Repeated identical error after an evidence-based correction:** stop the same operation. Change approach only when current evidence supports it; otherwise report the unresolved blocker.

## `Ad … is missing current creative`

In the October 5 verified case, 25 existing ads were labeled **Draft**. Their campaign wizard contained title/copy/images, but importing their populated IDs failed on every row with this error. A one-ad test using the exact native nine-column export failed too. Thus removing the template's `adgroup_name` column was not a repair.

The evidence is consistent with a difference between draft creative data and the importer’s current-creative relationship. That is an inference, not a confirmed backend diagnosis. Do not promise this error always has the same cause.

If the existing editor can perform the requested in-place update, prefer that when preserving IDs is necessary. Do not save or publish a whole campaign merely to test whether the importer will start working.

### Proven replacement path, when within scope

1. Confirm every affected original is inactive and belongs to the intended campaign. Export and preserve its ID, group, name, title, copy, destination, and image reference. Establish that user authorization covers replacing the failed records, not just in-place updates.
2. Make a **one-row paused create test**: same group and creative fields, blank `ad_id`. Keep this as an intermediate file. This creates a second object; it does not repair the original Draft.
3. Submit once. Require a successful completion and saved-row readback. Export the new native ID. If it fails or its result is unknown, reconcile before retrying; do not begin the remaining batch.
4. Exclude the successful test row. Submit only the remaining confirmed failed originals as paused creations, once. Handle any partial result per the rules above.
5. Export only the new replacements. Reconcile by `(ad_group_id, ad_name)` and exact creative fields; reject ambiguous exports containing both old and new versions. Pass the original failed CSV as `--exclude-original-ids` so a mistakenly selected original cannot be accepted as a replacement. Retain the old-to-new mapping.
6. Populate all new IDs in the final ten-column CSV. Validate in update mode, then upload this complete final file once if the task requires proof that the reusable CSV works. Its preview must show **Creates 0 / Updates N**; require **Passing N / Failed 0**.
7. Reload and confirm expected new/old counts and off switches. Report retained originals explicitly. Any archival/deletion remains a separate action under the applicable permission rules. Do not claim the originals were fixed or removed.

Observed outcome: one create passed, remaining24 creates passed, then the complete25-row populated-ID update passed25/0. The account retained25 new paused ads plus25 old inactive Drafts. Only `ad_id` changed in the final file; copy, image IDs, groups, and template headers were preserved.

Example local reconciliation from the skill directory:

```sh
python3 scripts/ad_csv.py reconcile \
  /absolute/path/original-failed.csv \
  /absolute/path/new-ads-native-export.csv \
  /absolute/path/ads-final.csv \
  --exclude-original-ids /absolute/path/original-failed.csv \
  --map-output /absolute/path/replacement-id-map.json
```

This helper only writes local output. Excluded IDs are rejected, not filtered automatically; re-export the right selection when it rejects old records. It refuses to overwrite inputs, and refuses to replace an existing output unless `--force` is supplied. Ordinary new-ad reconciliation can omit the exclusions when there are no originals.

## Limits of the repair

Replacement IDs change ad identity. Per-ad tracking, historical performance, review state, and other fields absent from the CSV are not automatically transferred. Check those separately if needed for launch. Parent budget/targeting and any draft-vs-published configuration discrepancies also remain separate. Report import success accurately without claiming launch readiness or serving eligibility.
