# Recovery and verification

Use these rules to reconcile uncertain outcomes before another mutation. The dated observations are failure examples, not permanent platform behavior.

## Interrupted or partial creation

1. Preserve the intended manifest, last confirmed save, object IDs if exposed, and exact error. Do not create replacement objects yet.
2. Inspect the current wizard, campaign list or identified saved draft. Determine which campaign/group/ad objects actually exist and which fields are complete. A toast alone does not identify the final saved state.
3. A newer, complete reopened readback supersedes an earlier error: do not mutate an already reconciled build. Otherwise, if the original wizard reports a child still saving, let that save settle. Retry **that same draft save** at most once only if an unresolved save failure remains, then reopen and compare before any additional creation.
4. If the same failure recurs without progress, stop that retry path. Preserve the draft and report the precise unresolved item. Continue independent copy/asset work if needed.
5. If the wizard is gone, resume the matching existing draft. Create a missing child only after confirming its absence; do not create an entire replacement campaign to recover one uncertain ad.

October 5, 2026: one 25-ad build returned a 409 “draft child is still being saved” for one ad. Retrying the same Save as draft completed the build; reopening confirmed all children and exactly one new campaign. A lingering old error notification was not sufficient evidence of current failure, nor was it sufficient to ignore readback.

Do not use CSV import as an automatic draft-repair route. A later authorized import on that campaign returned “missing current creative” for existing draft IDs. Creating with blank IDs produced separate replacement records while the original drafts remained. That is a different operation requiring explicit replacement scope, mappings and duplicate reconciliation. This skill's normal recovery path is the existing browser draft, not blank-ID retries, publication, or deletion.

## Settings that appear not to persist

| Observation | Required response |
| --- | --- |
| Campaign table shows a different budget from reopened form/summary | Record both; verify level, type, currency and amount in the reopened settings. Reconcile before launch; do not replace the budget from a table display alone. |
| Text customization reopens On after saving Off | Make at most one deliberate re-save/reopen attempt after inspecting state. If it recurs, record actual On and the failed Off persistence. Do not promise exact reviewed wording will be preserved. |
| Start date/time changes or becomes invalid | Confirm account timezone and the intended start; do not silently launch now to clear validation. |
| Image preview has zero dimensions or incomplete loading | Wait for the existing load, then check that specific ad and preview. Do not immediately upload another asset or create another ad. |
| Field appears empty in a text snapshot | Read the native input value or switch state. `innerText()` omits many form values. |

The October 2026 draft table showed $0 while its reopened settings/summary retained $125 average daily. Text customization also repeatedly reopened On. These are dated observations to check for, not blanket claims about current drafts. If the user explicitly wants customization On, no Off test is needed.

If a required setting remains incompatible with the user’s instructions, leave the campaign safely unlaunched and report the specific conflict. A permitted, fully completed draft build can be delivered with a disclosed prelaunch issue; do not falsely mark the issue fixed.

## Verification strength

Use the manifest as expected state and collect actual saved state after reopening:

- Campaign identity and number of newly created campaigns. Avoid relying solely on an account-wide count that other activity can change.
- Actual group sections/IDs and child IDs/names. Prefixes alone do not prove parent association.
- Exact public titles, descriptions, URLs, tracking and context hints, including inherited settings where relevant.
- Image-to-variant mapping, visible content, dimensions and crop. Different source URLs prove distinct references, not a remote/local byte-hash match. Do not make that stronger claim without actually comparing bytes.
- All consequential campaign settings and the observed lifecycle state.

A read-only native export can supplement verification if the UI exposes it. Selecting Export is not completion: verify the downloaded artifact. Never re-import solely to test a readback. Browser media downloading is optional; if it hangs, recover the browser session using supported documentation and use visible preview evidence rather than making downloads a prerequisite for completion.

## Receipt contents

Keep the receipt compact and factual; adapt these fields to the actual task:

```text
verified_at; account name/id; campaign name/id/url
requested final state; actual saved state; published/enabled/serving separately
objective; conversion event/source if used
budget level/type/currency/amount; country/platform/audience/schedule settings
text customization: intended, reopened, discrepancy if any
groups: platform/local ID, name, expected and actual child IDs
ads: platform/local ID, parent, exact fields, image source/path/crop readiness
tracking and context hints, or paths to exact readback records
manifest and asset hashes; verification results and limitations
save errors/recovery attempted; unresolved differences; screenshot paths
```

Do not put cookies, auth tokens, or signed media URL query strings in receipts or skill files. Leave unexposed identifiers unknown. A verified account link plus campaign name is better than an invented campaign URL.

Final wording should distinguish **prepared**, **saved draft**, **published**, **in review**, **approved**, **enabled**, and **serving**. Report only the states actually observed. Save a current screenshot after the final browser mutation and embed it in the response. Preserve original errors as historical evidence when useful; do not present a stale error screenshot as final confirmation.
