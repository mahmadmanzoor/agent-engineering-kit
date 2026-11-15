# Mobile releases: the two stores and OTA patches

## Side by side

| Topic | Google Play | Apple App Store |
|---|---|---|
| Test channel | Internal testing: up to 100 testers, live in minutes. Then closed or open testing. Then production. | TestFlight. Internal testers get a build at once; external testers wait for a short beta review. |
| Gradual release | Staged rollout to 10%, 50%, 100% of users. Halt at any point; people who updated keep the build. | Phased release: 1%, 2%, 5%, 10%, 20%, 50%, 100% over 7 days. Pause up to 30 days, or release to all. Manual updates still work. |
| Version numbers | `versionCode` strictly increases. `versionName` is the semantic version users see. | Build number increases within each version. Marketing version is semantic. |
| First health check | Pre-launch report, then Android vitals (crash rate, ANR rate). | Watch crash logs and diagnostics after release. |
| Permissions | New permissions and background location need the Data safety form. A few need a declaration. | Each permission (camera, photos, location, microphone, contacts) needs an Info.plist purpose string a reviewer will accept. A missing string crashes the app at the prompt. Add review notes for new usage descriptions and background modes. |
| Privacy disclosure | Privacy policy URL for apps with personal or sensitive data and for most permissions. | Privacy policy URL in App Store Connect. Privacy labels must match what the build really collects, crash logs and diagnostics included. |
| Signing | Keep the upload key in CI secrets, never in the repo. Play App Signing holds the app signing key. | Distribution certificate plus provisioning profiles, or automatic signing. CI uses an App Store Connect API key kept as a secret. Needs macOS; a hosted macOS runner is fine. |

**One Play trap for first releases.** A new personal developer account must run a closed test with at least 12 testers for 14 days before it can ask for production access. Schedule that time into the plan.

## OTA patch tools

What each tool can and cannot deliver:

- **Shorebird (Flutter).** Commands: `shorebird release`, `shorebird patch`.
  - Delivers Dart code changes to a release built with Shorebird.
  - Does not deliver native code, plugins, permissions, engine upgrades, or assets absent from the release.
  - Only releases made with `shorebird release` can receive patches.
- **Expo Updates / EAS Update (React Native or Expo).**
  - Delivers the JS bundle and assets, for a matching runtime version.
  - Does not deliver native modules, permissions or SDK upgrades. For those, bump `runtimeVersion` and do a store release.
- **CodePush and successors (React Native).**
  - Delivers the JS bundle and assets.
  - Does not deliver native code.

Whatever the tool:

1. Make the store build with the OTA tool's release command. Otherwise patches cannot find it.
2. Send the patch to staging first, try it on a device, and only then promote it.
3. The stores accept updates to interpreted code that leave the app's main purpose unchanged. Do not use a patch to add a feature that would have needed review.
4. The patch has to work with the native code already installed. When in doubt, use a store release.

## Undoing a bad release

1. **Play.** Halt the staged rollout. Upload a fixed build with a higher `versionCode`.
2. **App Store.** Pause the phased release. Submit a fixed build; critical fixes can ask for expedited review.
3. **OTA.** Use the tool's console or CLI to revert to the previous patch, or publish the earlier good code as a new patch.
