# Ad CSV schema and browser details

Snapshot verified October 5, 2026. Current platform UI and fresh native exports take precedence over this snapshot.

## Exact template

```csv
ad_id,ad_group_id,adgroup_name,ad_name,status,title,copy,link,image_url,image_file_id
```

| Field | Use |
| --- | --- |
| `ad_id` | Existing native ID updates that ad; blank creates a new ad. |
| `ad_group_id` | Existing target parent group ID; verify its campaign/account. |
| `adgroup_name` | Preserve the supplied template field. It was absent from the nine-column native export; that was not the cause of the observed error. |
| `ad_name` | Stable internal name. Reconcile jointly with group ID. |
| `status` | Lowercase `paused` was accepted and is the default for new imports. Preserve intentional existing states. |
| `title` | Observed importer range 3–50 characters. |
| `copy` | Maximum 100 characters in the observed flow. |
| `link` | Valid, reachable landing URL. The helper conservatively requires HTTPS. |
| `image_url` | Supported public direct-image URL when using URL-based assets. Not a local path or authenticated preview. |
| `image_file_id` | Native image asset identifier from the target account. With a verified file ID, blank `image_url` worked. Do not invent file IDs from filenames. |

Native exports can omit the display-name metadata column. Do not infer that all supplied templates should be reduced to nine columns. Preserve the current chosen import schema. The local helper intentionally supports this ten-column input plus a nine- or ten-column native reconciliation export.

Image size/format rules may change. Check the current upload UI and template. Successful reuse of an already uploaded file does not prove that every new file of that size is acceptable. Do not silently recompress approved artwork just because an older help page has a different limit.

## Native browser sequence

- Select the intended rows, then **Export selected resources → Export for edit**. Verify a downloaded file actually exists. An export menu click alone is not an export receipt.
- Open **Create → Upload bulk**. The Ads tab opened in **Ad** mode during the verified run; the Campaigns tab opened in bulk-workbook mode. Inspect rather than assume the current mode.
- **Upload CSV file → Import file → preview → Upload → Upload complete**. Labels may change; use fresh visible UI state.
- Inspect preview fields **Total / Valid / Uploadable / Creates / Updates**, then final **Passing / Failed / Total**. Preview validation did not catch the observed existing-Draft error.
- Downloads appeared in the configured Downloads directory in the verified run. A download-event wait once stalled even though the export completed. Before retrying an export, inspect the recent download/file and verify its scope; do not select the first old file with a similar name.

With documented CUA Playwright file chooser support, register the chooser before clicking:

```js
const chooserPromise = tab.playwright.waitForEvent('filechooser', {timeoutMs: 10000});
await tab.playwright.getByRole('button', {name: 'Upload CSV file', exact: true}).click();
const chooser = await chooserPromise;
await chooser.setFiles(['/absolute/path/ads.csv']);
await tab.getAXState();
```

Use only APIs exposed by the current tool documentation. Do not bypass the UI with guessed private endpoints or hidden browser state.

### Selecting replacement rows accurately

During recovery, old Draft and new paused rows may have identical names. Select by verified IDs when exposed; otherwise combine campaign/group scope with exact status cells and reconcile the resulting native export. Avoid substring filtering such as `hasNotText: 'Draft'`: case-insensitive substring matching also excluded real ads containing “draft” in their copy. An exact `Draft` status descendant filter worked:

```js
const rows = tab.playwright.getByRole('row').filter({
  hasText: expectedCampaignName,
  hasNot: tab.playwright.getByText('Draft', {exact: true})
});
// Inspect count and identities before selecting/exporting.
```

This is a pattern for an observed table, not a universal locator. Group scopes and native IDs still matter. Record the exact selection before exporting; never automatically pick the first name match.

## Primary documentation and evidence

- [Edit Campaigns](https://help.openai.com/en/articles/20001215-edit-campaigns), checked October 5, 2026: export-for-edit workflow, object types, and blank-ID create semantics.
- [Bulk Upload Campaign Schema Checklist](https://help.openai.com/en/articles/20001218-bulk-upload-campaign-schema-checklist), checked October 5, 2026: title/copy limits, public asset access, and uniqueness/format validation. Its full-workbook notes do not add extra header/comment rows to this ad-only CSV.
- Historical project case, October 5, 2026: 25 populated-ID draft updates failed; an authorized one-row paused replacement followed by 24 paused replacements succeeded, and the final populated-ID update passed 25/0. The original 25 inactive Draft records remained. Private account receipts are excluded from this public kit; the transferable recovery procedure is in [recovery.md](recovery.md). This is a dated case, not current account state or a universal fix.
