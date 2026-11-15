# Browser workflow

This is a navigation guide, not a fixed selector script. Labels and capabilities below were observed in Ads Manager in October 2026. Inspect the live UI each time.

## Start in the right surface

Use the first-call entrypoint required by `mcp__cua_repl`: get the user-mentioned tab, select a known Ads Manager tab, or create an in-app tab for `https://ads.openai.com/`. The first invocation must contain only that documented entrypoint. Read its returned documentation before continuing. After context compaction, restore the current browser documentation before resuming.

Reuse the tab handle. Use `getAXState()` or a DOM snapshot to establish the current controls, and screenshots when visual inspection is needed. Normal authentication may be resumed; hand off unavailable password/MFA input and then observe the authenticated account. A login or code form is not proof of authentication.

Confirm the account name and any exposed account identifier. On the Campaigns page, look for a matching saved draft and evidence of previous work. Record the relevant existing objects, not merely the account-wide count. Do not assume the last account or campaign in a local receipt is still current.

## Campaign settings

Observed entry: **Create → Create campaign**. An existing draft opens through **Finish draft** or its campaign name. The dialog can still be titled **New campaign** while editing an existing draft; that title alone does not mean it is a new object.

Inspect and fill the current form:

| Area | What to establish |
| --- | --- |
| Name/type | Requested name and appropriate supported type; avoid unintentionally creating product-feed campaigns |
| Objective | Requested outcome and supported measurement; some objective choices cannot be changed after creation |
| Conversion event | Correct event/source when applicable; do not infer successful tracking from an event's name |
| Locations | Explicitly include requested countries; excluding others alone does not establish US-only targeting |
| Platforms/audiences | Use requested restrictions; do not invent custom audiences |
| Budget | Amount, currency, level, daily/total and any displayed limits; “average daily” is not a hard daily cap |
| Schedule | Account timezone, start/end, and any first-campaign UI limitation; do not publish to unlock scheduling |
| Tracking | Supported macros and intended inheritance across campaign, group and ad levels |
| Text customization | Set according to the brief and verify again after reopening |

Budget controls are account/product-version dependent. In the October 2026 observed build, budgets belonged to the campaign. Get a user decision if this cannot enforce their requested group-level allocation. Never silently multiply a budget, change campaign count, or interpret $25 each as $25 shared.

Keep a clean destination plus the dedicated tracking fields when supported and consistent with the user's setup. If the current UI requires parameters in the URL instead, preserve the user's destination and check the final result for duplicate or conflicting keys. Read supported macro labels; do not invent macros.

## Groups and ads

Observed wizard navigation: campaign, **Create Ad Group & Ads**, then **Campaign summary**. Each group has **All Ads**, individual ad entries, and **New Ad**; **New Ad Group** adds another group. Repeated button labels must be scoped to the intended group or dialog.

For each group:

1. Confirm the group name, destination, bid strategy and any conversion/billing settings actually exposed.
2. Fill tracking and context hints. Use distinct phrases describing offering, use case or customer need; inspect whether adding a hint requires an explicit Add/Enter action.
3. Add each intended ad in that group. Stable short variant IDs in internal names make reconciliation easier; they need not appear in public copy.
4. Replace generated/prefilled public fields with the approved exact title/description. Check the current character counters and validation messages.
5. Set the intended destination and ad-level tracking. Do not rely on inheritance without verifying what the saved editor shows.
6. Select the image for that exact variant and confirm its preview/crop before moving to the next ad.

Do not use “duplicate” blindly: it may copy destination, tracking, image or parent group unexpectedly. When duplication is useful, verify all fields that should differ and the resulting object count.

## UI patterns

Use role/name/label/placeholder locators from observed state. Examples below assume `ads` is an already-bound tab and the named controls have just been observed. They are not a substitute for discovering changed labels.

```javascript
// A native editable field's value is separate from its visible surrounding text.
const fields = await ads.playwright
  .getByRole('dialog', { name: 'New campaign', exact: true })
  .getByRole('textbox')
  .evaluateAll(elements => elements.map(e => ({
    label: e.getAttribute('aria-label'),
    placeholder: e.getAttribute('placeholder'),
    value: e.value
  })));
nodeRepl.write(fields);
```

Read `file-uploads` documentation through the current browser runtime before the first upload. Use the documented file chooser API with an absolute local image path and the actual observed upload control. Complete any native crop/confirm dialog. Do not try to set arbitrary page state or upload through a hidden endpoint.

Read-only DOM evaluation can inspect an already-observed preview image. Store unsigned source identity rather than signed query strings:

```javascript
const loaded = await ads.playwright
  .getByRole('button', { name: 'Edit image', exact: true })
  .locator('img')
  .evaluate(img => ({
    sourcePath: new URL(img.src).origin + new URL(img.src).pathname,
    width: img.naturalWidth,
    height: img.naturalHeight,
    complete: img.complete,
    cropStyle: img.getAttribute('style')
  }));
nodeRepl.write(loaded);
```

Use this only if the live preview has that structure. Nonzero loaded dimensions and `complete` help establish readiness; screenshot inspection establishes the actual visible content and crop. If the image is still loading, allow that transition to finish and recheck that entry, rather than declaring an upload failure. Distinct images are required only when the brief calls for them; one approved image may intentionally serve multiple copy variants.

Serialize field changes, uploads, group changes and saves. A local asset review can run in parallel. Do not issue concurrent writes against the same wizard or object.

## Save and review

**Save as draft** may save asynchronously and close the dialog. **Close creation wizard** also triggered autosave in the observed build; do not use it as a discard action. Read the live result instead of assuming either behavior is permanent.

Wait for the saving state to resolve through supported state checks or element-state waits. A new save click while the first is in progress is not a recovery strategy. Follow [recovery-and-verification.md](recovery-and-verification.md) if an error or partial result appears.

After save, reopen the identified draft. Use **Campaign summary** to inspect actual group sections and counts. Navigation order may differ from creation order; compare IDs/membership, not row positions. For large builds, collect fields into a readback file and compare against the manifest locally, while visually inspecting the previews. Recheck only failures/incomplete loads after a full pass.

## Official references

Consult the current UI first for account-specific availability; use official documentation if meaning or limits are unclear. References checked October 5, 2026:

- [Create campaigns](https://help.openai.com/en/articles/20001210-create-campaigns-for-chatgpt-ads): objectives, campaign budgets, schedules and locations.
- [Create ad groups](https://help.openai.com/en/articles/20001211-create-ad-groups-for-chatgpt-ads): group organization and context hints.
- [Create ads](https://help.openai.com/en/articles/20001212-create-ads-for-chatgpt-ads): creative fields and landing-page alignment.
