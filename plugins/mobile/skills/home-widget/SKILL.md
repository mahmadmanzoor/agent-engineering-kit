---
name: home-widget
description: "Add or change a glanceable surface outside the app: a home or lock screen widget, a live status display, or a quick-settings tile. Every state gets built. The app writes a compact snapshot holding ready-made state and a staleAfter time, so one rule decides freshness. Refreshes never hit the network, actions reuse the app's code, the lock screen stays private, and each state is tested in code and on a device. Use when building any glanceable surface. Say: '/mobile:home-widget', 'add a widget', 'lock screen widget', 'live activity', 'quick settings tile'."
argument-hint: "[name of the widget, tile or live activity]"
license: MIT
metadata:
  version: "1.0.0"
  model: sonnet
  effort: medium
---

# Home widget

Build the surface named in `$ARGUMENTS`: a widget, live status display or tile. With no argument, list the glanceable-surface designs and ask the user to pick.

**Run on:** sonnet at medium. The pattern is fixed, and snapshot tests check it.

## Use it when
- You build or change any glanceable surface outside the app.

**Not for:** screens inside the app (`design-to-screen`), or a rule the widget depends on (`shared-core`).

## Before you start
Read `AGENTS.md`, `CLAUDE.md`, the widget design, and the native rules (`shared-core`, `app-rules`). Find out how the app hands data to native extensions today: a shared container, shared preferences or a bridge package. Find the freshness rule that already exists in the app's domain. Platform notes: [references/android.md](references/android.md), [references/ios.md](references/ios.md).

## Steps
1. **Enumerate the states.** Build each one that applies. A notes app with a "pinned note" widget shows how they look.
   - **Live.** The current data, plus its age.
   - **Stale.** The age and the reason, for example "Offline since 18:58". Never fake a live state.
   - **Paused.** A plain paused look with an action to resume.
   - **Off or not set up.** Says what is switched off and how to repair it. A tap opens the app.
   - **Urgent takeover.** Replaces the normal content when something needs attention right now.
   - **Hidden on the lock screen.** Shows no names, places or content, because the user chose privacy for that screen.
   - **Signed out.** A sign-in prompt. No stale personal data stays visible.

   **Stop if:** a state has neither a design nor an agreed fallback.

2. **Plan the data flow.**
   - The app writes a small, versioned snapshot into storage shared with the extension, then asks the system to reload the widget. The snapshot holds display labels, a state per item and ages. Precise personal data stays out, unless the widget really needs it. Then use a reduced version.
   - Keep the freshness rule out of widget code. For each item, the app decides the state using its own domain rule, then stores that state in the snapshot next to `staleAfter`, the moment a live entry becomes stale. The widget draws the state it receives and flips from live to stale at `staleAfter`. A time limit written in widget code would be a second copy, and copies drift.
   - If a decision cannot be precomputed by the app, put it in the shared core with tests. Never put it in widget code.
   - A widget never calls the network on each refresh. The app drives updates, triggered by new data, a push or background work, and stays inside the platform's refresh budget.
   - When the user taps a control (toggle, start, open), route the call into the app's existing code. Copying that logic is wrong.
   - Wipe the snapshot on sign-out.

3. **Write the tests.**
   - App side: unit tests for the snapshot builder, one per state, asserting the exact JSON. Cover urgent takeover, hidden on lock screen and `staleAfter`.
   - Native side: a preview for each state, and a test that parses every snapshot version the widget could meet. An older app build may have written it.
   - Accessibility basics: labels, contrast and large text (`a11y-audit` in `check`).

4. **Build it** following the platform notes. Keep names and states identical on both platforms. Map design tokens from the app theme.

5. **Try it on devices** (`device-test`), on a real Android phone and a real iPhone.
   - Add the widget.
   - Use its toggle.
   - Lock the phone and check the privacy state.
   - Trigger the urgent state, then return to normal.
   - Kill the app. The widget must turn stale with a reason, not stay live.

   Record the results in the PR. Widgets go out in a store release.

   **Stop if:** a state has not been seen on a device and is not listed as open under the project's device-test batching rule.

## Done when
- [ ] Every state passes its code test (paste the output) and was seen on a device, or is listed as open.
- [ ] The snapshot carries precomputed state and `staleAfter`.
- [ ] Widget code holds no business rule and makes no network call.

## Never
- Put a business rule in widget code, or call the network on each refresh.
- Put personal data on the lock screen without the user's choice.
- Label data "live" when the app has not confirmed it is fresh.

## Next
- **Comes from:** `build` (`ship`), `design-to-screen` (`mobile`)
- **Leads to:** `shared-core` for any decision; `device-test`; `release` (`ship`) for the store release
